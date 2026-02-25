from src.utils.parsers.atom.exceptions import AtomSyntaxError
from src.utils.parsers.atom.AtomTypeConverter import AtomTypeConverter


class AtomParser:
	"""
	Parser for King's Bounty atom file format
	"""

	def __init__(self, convert_types: bool = True):
		"""
		Initialize atom parser

		:param convert_types:
			Whether to automatically convert types (bool, int, float)
		"""
		self._convert_types = convert_types
		self._pos = 0
		self._tokens = []

	def parse(self, content: str) -> dict | list:
		"""
		Parse atom format string to Python dict or list

		:param content:
			Atom format content string
		:return:
			Parsed structure as dict or list
		"""
		if content.startswith('\ufeff'):
			content = content[1:]

		cleaned = self._remove_comments(content)
		self._tokens = self._tokenize(cleaned)
		self._pos = 0

		result = {}
		while self._pos < len(self._tokens):
			token = self._tokens[self._pos]
			if token == '{':
				self._pos += 1
				continue
			if self._peek() == '{':
				block_name = token
				self._pos += 1
				block_data = self._parse_block()
				self._add_to_dict(result, block_name, block_data)
			else:
				self._pos += 1

		return result

	def _remove_comments(self, content: str) -> str:
		"""
		Remove line and inline comments

		:param content:
			Raw content string
		:return:
			Content with comments removed
		"""
		lines = []
		for line in content.split('\n'):
			if line.strip().startswith('//'):
				continue
			comment_pos = line.find('//')
			if comment_pos != -1:
				line = line[:comment_pos]
			if line.strip():
				lines.append(line)
		return '\n'.join(lines)

	def _tokenize(self, content: str) -> list[str]:
		"""
		Split content into tokens

		:param content:
			Cleaned content string
		:return:
			List of tokens
		"""
		tokens = []
		current = ''
		after_equals = False

		for char in content:
			if char in '{}=':
				if current.strip():
					tokens.append(current.strip())
					current = ''
				elif after_equals and char != '=':
					tokens.append('')

				tokens.append(char)
				after_equals = (char == '=')
				current = ''

			elif char in ' \t\n\r':
				if current.strip():
					tokens.append(current.strip())
					after_equals = False
					current = ''
				elif after_equals:
					tokens.append('')
					after_equals = False
				current = ''

			else:
				current += char
				after_equals = False

		if current.strip():
			tokens.append(current.strip())
		elif after_equals:
			tokens.append('')

		return tokens

	def _peek(self, offset: int = 1) -> str | None:
		"""
		Peek at token ahead without consuming

		:param offset:
			Number of positions to look ahead
		:return:
			Token at position or None
		"""
		pos = self._pos + offset
		if pos < len(self._tokens):
			return self._tokens[pos]
		return None

	def _parse_block(self) -> dict | list:
		"""
		Parse block content between braces

		:return:
			Parsed block as dict or list (if contains only unnamed blocks)
		"""
		if self._tokens[self._pos] != '{':
			context = self._get_error_context()
			raise AtomSyntaxError(
				f"Expected {{, got {self._tokens[self._pos]}\n"
				f"Context: {context}"
			)

		self._pos += 1
		block_data = {}
		unnamed_blocks = []

		while self._pos < len(self._tokens) and self._tokens[self._pos] != '}':
			token = self._tokens[self._pos]

			if token == '{':
				unnamed_block = self._parse_block()
				unnamed_blocks.append(unnamed_block)
				continue

			next_token = self._peek()

			if next_token == '=':
				key = token
				self._pos += 2

				if self._pos >= len(self._tokens):
					block_data[key] = ''
				elif self._tokens[self._pos] == '{':
					nested_data = self._parse_block()
					self._add_to_dict(block_data, key, nested_data)
				else:
					value = self._tokens[self._pos]
					if self._convert_types and value != '':
						value = AtomTypeConverter.convert(value)
					block_data[key] = value
					self._pos += 1

			elif next_token == '{':
				block_name = token
				self._pos += 1
				nested_data = self._parse_block()
				self._add_to_dict(block_data, block_name, nested_data)

			else:
				self._pos += 1

		if self._pos >= len(self._tokens):
			context = self._get_error_context()
			raise AtomSyntaxError(
				f"Unexpected end of file, expected }}\n"
				f"Context: {context}"
			)

		self._pos += 1

		if unnamed_blocks and not block_data:
			return unnamed_blocks
		elif unnamed_blocks:
			for idx, unnamed_block in enumerate(unnamed_blocks):
				self._add_to_dict(block_data, str(idx + 1), unnamed_block)

		return self._detect_list_structure(block_data)

	def _add_to_dict(
		self,
		target: dict,
		key: str,
		value: any
	) -> None:
		"""
		Add key-value pair to dict, handling duplicates

		:param target:
			Target dictionary
		:param key:
			Key to add
		:param value:
			Value to add
		"""
		if key in target:
			if not isinstance(target[key], list):
				target[key] = [target[key]]
			target[key].append(value)
		else:
			target[key] = value

	def _detect_list_structure(self, block_data: dict) -> dict | list:
		"""
		Detect if block should be converted to list

		:param block_data:
			Block dictionary
		:return:
			List if all keys are sequential numeric, otherwise dict
		"""
		if not block_data:
			return block_data

		keys = list(block_data.keys())
		try:
			indices = [int(k) for k in keys]
		except ValueError:
			return block_data

		indices.sort()
		if indices == list(range(1, len(indices) + 1)):
			return [block_data[str(i)] for i in indices]

		return block_data

	def _get_error_context(self) -> str:
		"""
		Get surrounding tokens for error messages

		:return:
			Context string with visual pointer
		"""
		start = max(0, self._pos - 5)
		end = min(len(self._tokens), self._pos + 5)
		context_tokens = self._tokens[start:end]
		pointer_pos = min(self._pos - start, len(context_tokens))

		tokens_str = ' '.join(context_tokens)
		pointer = ' ' * sum(len(t) + 1 for t in context_tokens[:pointer_pos]) + '^'
		return f"{tokens_str}\n{pointer}"
