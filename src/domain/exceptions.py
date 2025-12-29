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
