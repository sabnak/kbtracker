from src.utils.atom.exceptions import AtomSyntaxError
from src.utils.atom.AtomTypeConverter import AtomTypeConverter


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
		for char in content:
			if char in '{}=':
				if current.strip():
					tokens.append(current.strip())
				tokens.append(char)
				current = ''
			elif char in ' \t\n':
				if current.strip():
					tokens.append(current.strip())
				current = ''
			else:
				current += char

		if current.strip():
			tokens.append(current.strip())

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

	def _parse_block(self) -> dict:
		"""
		Parse block content between braces

		:return:
			Parsed block as dict
		"""
		if self._tokens[self._pos] != '{':
			raise AtomSyntaxError(f"Expected {{, got {self._tokens[self._pos]}")

		self._pos += 1
		block_data = {}

		while self._pos < len(self._tokens) and self._tokens[self._pos] != '}':
			token = self._tokens[self._pos]

			if token == '{':
				self._pos += 1
				continue

			next_token = self._peek()

			if next_token == '=':
				key = token
				self._pos += 2
				if self._pos < len(self._tokens) and self._tokens[self._pos] == '{':
					nested_data = self._parse_block()
					self._add_to_dict(block_data, key, nested_data)
				else:
					value = self._tokens[self._pos]
					if self._convert_types:
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
			raise AtomSyntaxError("Unexpected end of file, expected }")

		self._pos += 1
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
