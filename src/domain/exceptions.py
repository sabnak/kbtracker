class KBTrackerException(Exception):
	"""
	Base exception for all KB Tracker application errors
	"""

	def __init__(self, message: str, original_exception: Exception | None = None):
		self._message = message
		self._original_exception = original_exception
		super().__init__(message)

	@property
	def message(self) -> str:
		return self._message

	@property
	def original_exception(self) -> Exception | None:
		return self._original_exception


class RepositoryException(KBTrackerException):
	"""
	Base exception for all repository-related errors
	"""
	pass


class DuplicateEntityException(RepositoryException):
	"""
	Raised when attempting to create a duplicate entity
	"""

	def __init__(
		self,
		entity_type: str,
		identifier: str,
		original_exception: Exception | None = None
	):
		self._entity_type = entity_type
		self._identifier = identifier
		message = f"{entity_type} with identifier '{identifier}' already exists"
		super().__init__(message, original_exception)

	@property
	def entity_type(self) -> str:
		return self._entity_type

	@property
	def identifier(self) -> str:
		return self._identifier


class EntityNotFoundException(RepositoryException):
	"""
	Raised when an entity is not found
	"""

	def __init__(
		self,
		entity_type: str,
		identifier: str | int,
		original_exception: Exception | None = None
	):
		self._entity_type = entity_type
		self._identifier = identifier
		message = f"{entity_type} with identifier '{identifier}' not found"
		super().__init__(message, original_exception)

	@property
	def entity_type(self) -> str:
		return self._entity_type

	@property
	def identifier(self) -> str | int:
		return self._identifier


class DatabaseOperationException(RepositoryException):
	"""
	Raised when a database operation fails
	"""

	def __init__(
		self,
		operation: str,
		details: str,
		original_exception: Exception | None = None
	):
		self._operation = operation
		self._details = details
		message = f"Database operation '{operation}' failed: {details}"
		super().__init__(message, original_exception)

	@property
	def operation(self) -> str:
		return self._operation

	@property
	def details(self) -> str:
		return self._details


class InvalidPropbitException(KBTrackerException):
	"""
	Raised when an invalid propbit value is encountered
	"""

	def __init__(
		self,
		invalid_value: str,
		valid_values: list[str] | None = None,
		original_exception: Exception | None = None
	):
		self._invalid_value = invalid_value
		self._valid_values = valid_values

		if valid_values:
			message = (
				f"Invalid propbit value '{invalid_value}'. "
				f"Valid values: {', '.join(valid_values)}"
			)
		else:
			message = f"Invalid propbit value '{invalid_value}'"

		super().__init__(message, original_exception)

	@property
	def invalid_value(self) -> str:
		return self._invalid_value

	@property
	def valid_values(self) -> list[str] | None:
		return self._valid_values


class InvalidRegexException(KBTrackerException):
	"""
	Raised when an invalid regex pattern is provided
	"""

	def __init__(
		self,
		pattern: str,
		original_exception: Exception | None = None
	):
		self._pattern = pattern
		message = f"Invalid regex pattern: '{pattern}'"
		super().__init__(message, original_exception)

	@property
	def pattern(self) -> str:
		return self._pattern


class InvalidLocalizationTypeException(KBTrackerException):
	"""
	Raised when an invalid localization type value is encountered
	"""

	def __init__(
		self,
		invalid_value: str,
		valid_values: list[str] | None = None,
		original_exception: Exception | None = None
	):
		self._invalid_value = invalid_value
		self._valid_values = valid_values

		if valid_values:
			message = (
				f"Invalid localization type value '{invalid_value}'. "
				f"Valid values: {', '.join(valid_values)}"
			)
		else:
			message = f"Invalid localization type value '{invalid_value}'"

		super().__init__(message, original_exception)

	@property
	def invalid_value(self) -> str:
		return self._invalid_value

	@property
	def valid_values(self) -> list[str] | None:
		return self._valid_values
