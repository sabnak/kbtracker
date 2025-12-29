from fastapi.templating import Jinja2Templates


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
	- Preserves [d] as placeholder for in-game digits
	- Preserves <br> tags
	- Removes special characters like ^?^

	:param text:
		Raw text from game
	:return:
		HTML-formatted text
	"""
	if not text:
		return ""

	# Remove special characters like ^?^
	formatted = text.replace("^?^", "")

	# Replace BBCode bold tags
	formatted = formatted.replace("[s]", "<b>").replace("[/s]", "</b>")
	formatted = formatted.replace("[b]", "<b>").replace("[/b]", "</b>")

	# Replace BBCode underline tags
	formatted = formatted.replace("[u]", "<u>").replace("[/u]", "</u>")

	# Replace [sys] with styled span (for system/special text)
	formatted = formatted.replace("[sys]", '<span class="sys-text">')
	formatted = formatted.replace("[/sys]", "</span>")

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
