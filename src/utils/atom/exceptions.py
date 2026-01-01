class AtomParseError(Exception):
	"""
	Base exception for atom parsing errors
	"""
	pass


class AtomSyntaxError(AtomParseError):
	"""
	Exception raised when atom file has invalid syntax
	"""

	def __init__(self, message: str, line: int | None = None):
		"""
		Initialize syntax error with message and optional line number

		:param message:
			Error description
		:param line:
			Line number where error occurred
		"""
		self.line = line
		if line is not None:
			message = f"Line {line}: {message}"
		super().__init__(message)


class AtomEncodingError(AtomParseError):
	"""
	Exception raised when file encoding cannot be determined
	"""
	pass
