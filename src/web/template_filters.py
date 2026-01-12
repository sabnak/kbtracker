import re

from fastapi.templating import Jinja2Templates

from src.domain.app.interfaces.ITranslationService import ITranslationService


def format_price(value: int | None) -> str:
	"""
	Format price with thousand separators

	:param value:
		Price value
	:return:
		Formatted price string (e.g., "34 000")
	"""
	if value is None:
		return "0"
	return f"{value:,}".replace(",", " ")


def format_text(text: str | None) -> str:
	"""
	Format game text with HTML tags
	- Converts BBCode tags: [s], [b] to <b>, [u] to <u>, [sys] to <span class="sys-text">
	- Automatically closes unclosed BBCode tags
	- Preserves [d] as placeholder for in-game digits
	- Preserves <br> tags
	- Removes special characters like ^?^
	- Removes ^...^ pattern from beginning of text
	- Removes "Features:" prefix
	- Converts <color=R,G,B> tags to HTML span with inline style
	- Removes <gen=...> placeholder tags

	:param text:
		Raw text from game
	:return:
		HTML-formatted text with properly closed tags
	"""
	if not text:
		return ""

	# Remove ^...^ pattern from the beginning of the string
	formatted = re.sub(r'^\^[^^]+\^', '', text)

	# Remove "Features:" prefix (case-insensitive)
	formatted = re.sub(r'^Features:\s*', '', formatted, flags=re.IGNORECASE)

	# Remove special characters like ^?^
	formatted = formatted.replace("^?^", "")

	# Handle <color=...> tags - convert to span with inline style
	formatted = re.sub(r'<color=(\d+),(\d+),(\d+)>', lambda m: f'<span style="color: rgb({m.group(1)}, {m.group(2)}, {m.group(3)});">', formatted)
	formatted = formatted.replace('</color>', '</span>')

	# Remove <gen=...> tags (placeholders for in-game generated values)
	formatted = re.sub(r'<gen=[^>]+>', '', formatted)

	# Count unclosed tags BEFORE replacement
	# [u] tags
	u_unclosed = formatted.count("[u]") - formatted.count("[/u]")

	# [s] and [b] tags (both convert to <b>)
	bold_unclosed = (
		formatted.count("[s]") + formatted.count("[b]")
		- formatted.count("[/s]") - formatted.count("[/b]")
	)

	# [sys] tags
	sys_unclosed = formatted.count("[sys]") - formatted.count("[/sys]")

	# Replace BBCode bold tags
	formatted = formatted.replace("[s]", "<b>").replace("[/s]", "</b>")
	formatted = formatted.replace("[b]", "<b>").replace("[/b]", "</b>")

	# Replace BBCode underline tags
	formatted = formatted.replace("[u]", "<u>").replace("[/u]", "</u>")

	# Replace [sys] with styled span (for system/special text)
	formatted = formatted.replace("[sys]", '<span class="sys-text">')
	formatted = formatted.replace("[/sys]", "</span>")

	# Close unclosed tags
	if u_unclosed > 0:
		formatted += "</u>" * u_unclosed
	if bold_unclosed > 0:
		formatted += "</b>" * bold_unclosed
	if sys_unclosed > 0:
		formatted += "</span>" * sys_unclosed

	# [d] is kept as-is (placeholder for in-game digits)
	# <br> tags are already HTML, no conversion needed
	return formatted


def register_filters(templates: Jinja2Templates) -> None:
	"""
	Register all custom filters with Jinja2Templates instance

	:param templates:
		Jinja2Templates instance
	:return:
	"""
	templates.env.filters["format_price"] = format_price
	templates.env.filters["format_text"] = format_text


def install_translations(
	templates: Jinja2Templates,
	translation_service: ITranslationService
) -> None:
	"""
	Install translation functions in Jinja2 environment

	:param templates:
		Jinja2Templates instance
	:param translation_service:
		Translation service for i18n
	:return:
	"""
	templates.env.add_extension('jinja2.ext.i18n')
	templates.env.install_gettext_callables(
		gettext=translation_service.gettext,
		ngettext=lambda s, p, n: translation_service.gettext(s if n == 1 else p),
		newstyle=True
	)
