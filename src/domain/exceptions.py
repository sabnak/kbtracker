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
		original_exception: Exception | None = None,
		atom_kb_id: str = None
	):
		self._entity_type = entity_type
		self._identifier = identifier
		message = f"{entity_type} with identifier '{identifier}' not found. Atom kb_id: {atom_kb_id}"
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


class InvalidRegexPatternException(KBTrackerException):
	"""
	Raised when a regex pattern is missing required named groups
	"""

	def __init__(
		self,
		pattern: str,
		missing_group: str,
		original_exception: Exception | None = None
	):
		self._pattern = pattern
		self._missing_group = missing_group
		message = f"Regex pattern missing required named group '{missing_group}': {pattern}"
		super().__init__(message, original_exception)

	@property
	def pattern(self) -> str:
		return self._pattern

	@property
	def missing_group(self) -> str:
		return self._missing_group


class InvalidKbIdException(KBTrackerException):
	"""
	Raised when a kb_id doesn't match the required format
	"""

	def __init__(
		self,
		kb_id: str,
		source: str,
		original_exception: Exception | None = None
	):
		self._kb_id = kb_id
		self._source = source
		message = f"Invalid kb_id '{kb_id}' in {source}: must match pattern ^[-\\w]+$"
		super().__init__(message, original_exception)

	@property
	def kb_id(self) -> str:
		return self._kb_id

	@property
	def source(self) -> str:
		return self._source


class NoLocalizationMatchesException(KBTrackerException):
	"""
	Raised when no localization entries are found in a file
	"""

	def __init__(
		self,
		file_name: str,
		pattern: str,
		lang: str,
		original_exception: Exception | None = None
	):
		self._file_name = file_name
		self._pattern = pattern
		self._lang = lang
		message = f"No localization entries found in {lang}_{file_name}.lng using pattern: {pattern}"
		super().__init__(message, original_exception)

	@property
	def file_name(self) -> str:
		return self._file_name

	@property
	def pattern(self) -> str:
		return self._pattern

	@property
	def lang(self) -> str:
		return self._lang


class LocalizationNotFoundException(RepositoryException):
	"""
	Raised when required localization is not found
	"""

	def __init__(
		self,
		entity_type: str,
		kb_id: str,
		localization_key: str,
		original_exception: Exception | None = None
	):
		self._entity_type = entity_type
		self._kb_id = kb_id
		self._localization_key = localization_key
		message = (
			f"Required localization not found for {entity_type} '{kb_id}': "
			f"missing '{localization_key}'"
		)
		super().__init__(message, original_exception)

	@property
	def entity_type(self) -> str:
		return self._entity_type

	@property
	def kb_id(self) -> str:
		return self._kb_id

	@property
	def localization_key(self) -> str:
		return self._localization_key


class MetadataNotFoundException(RepositoryException):
	"""
	Raised when metadata is not found in the meta table
	"""

	def __init__(
		self,
		name: str,
		original_exception: Exception | None = None
	):
		self._name = name
		message = f"Metadata with name '{name}' not found"
		super().__init__(message, original_exception)

	@property
	def name(self) -> str:
		return self._name
