import traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError, HTTPException

from src.domain.exceptions import (
	DuplicateEntityException,
	EntityNotFoundException,
	DatabaseOperationException,
	InvalidRegexException,
	InvalidPropbitException,
	InvalidKbIdException,
	InvalidRegexPatternException,
	NoLocalizationMatchesException,
	LocalizationNotFoundException
)
from src.web.middleware.request_context import get_request_id


@dataclass
class ErrorDetail:
	"""
	Error detail information

	:param type:
		Exception class name
	:param message:
		Human-readable error message
	:param code:
		Application error code (e.g., "DUPLICATE_ENTITY")
	:param details:
		Exception-specific details (optional)
	"""
	type: str
	message: str
	code: str
	details: dict[str, Any] | None = None


@dataclass
class ErrorResponse:
	"""
	Structured API error response

	:param error:
		Error detail information
	:param timestamp:
		ISO 8601 timestamp of when error occurred
	:param request_id:
		Unique request identifier for tracking
	:param path:
		Request path where error occurred
	:param traceback:
		Full traceback lines for debugging
	"""
	error: ErrorDetail
	timestamp: str
	request_id: str
	path: str
	traceback: list[str]

	def to_dict(self) -> dict[str, Any]:
		"""
		Convert to dictionary for JSON serialization

		:return:
			Dictionary representation of error response
		"""
		result = asdict(self)
		result["error"] = asdict(self.error)
		return result


# Mapping of exception types to error codes
ERROR_CODE_MAPPING: dict[type, str] = {
	DuplicateEntityException: "DUPLICATE_ENTITY",
	EntityNotFoundException: "ENTITY_NOT_FOUND",
	DatabaseOperationException: "DATABASE_ERROR",
	InvalidRegexException: "INVALID_REGEX",
	InvalidPropbitException: "INVALID_PROPBIT",
	InvalidKbIdException: "INVALID_KB_ID",
	InvalidRegexPatternException: "INVALID_REGEX_PATTERN",
	NoLocalizationMatchesException: "NO_LOCALIZATION",
	LocalizationNotFoundException: "LOCALIZATION_NOT_FOUND",
	HTTPException: "HTTP_ERROR",
	RequestValidationError: "VALIDATION_ERROR",
	Exception: "INTERNAL_ERROR"
}


# Mapping of exception types to HTTP status codes
STATUS_CODE_MAPPING: dict[type, int] = {
	DuplicateEntityException: 409,
	EntityNotFoundException: 404,
	DatabaseOperationException: 500,
	InvalidRegexException: 400,
	InvalidPropbitException: 400,
	InvalidKbIdException: 400,
	InvalidRegexPatternException: 400,
	NoLocalizationMatchesException: 404,
	LocalizationNotFoundException: 404,
	RequestValidationError: 422,
	Exception: 500
}


def format_traceback(exc: Exception) -> list[str]:
	"""
	Extract and format exception traceback

	:param exc:
		Exception instance to extract traceback from
	:return:
		List of traceback lines for JSON serialization
	"""
	return traceback.format_exception(type(exc), exc, exc.__traceback__)


def _extract_exception_details(exc: Exception) -> dict[str, Any] | None:
	"""
	Extract exception-specific details for structured error response

	:param exc:
		Exception instance to extract details from
	:return:
		Dictionary of exception details or None
	"""
	# Extract details from domain exceptions
	if isinstance(exc, (DuplicateEntityException, EntityNotFoundException)):
		return {
			"entity_type": exc.entity_type,
			"identifier": str(exc.identifier)
		}

	if isinstance(exc, DatabaseOperationException):
		return {
			"operation": exc.operation,
			"details": exc.details
		}

	if isinstance(exc, (InvalidRegexException, InvalidRegexPatternException)):
		return {
			"pattern": exc.pattern if hasattr(exc, "pattern") else None
		}

	if isinstance(exc, InvalidKbIdException):
		return {
			"kb_id": exc.kb_id if hasattr(exc, "kb_id") else None
		}

	if isinstance(exc, InvalidPropbitException):
		return {
			"propbit": exc.propbit if hasattr(exc, "propbit") else None
		}

	if isinstance(exc, HTTPException):
		return {
			"status_code": exc.status_code,
			"detail": exc.detail
		}

	if isinstance(exc, RequestValidationError):
		return {
			"errors": [
				{
					"loc": list(error["loc"]),
					"msg": error["msg"],
					"type": error["type"]
				}
				for error in exc.errors()
			]
		}

	return None


def create_error_response(request: Request, exc: Exception) -> ErrorResponse:
	"""
	Factory function to create structured error response

	:param request:
		FastAPI request object
	:param exc:
		Exception instance to create response for
	:return:
		Structured error response object
	"""
	# Determine error code
	exc_type = type(exc)
	error_code = ERROR_CODE_MAPPING.get(exc_type, "INTERNAL_ERROR")

	# For base exception types, check if it's a subclass
	if error_code == "INTERNAL_ERROR":
		for exc_class, code in ERROR_CODE_MAPPING.items():
			if isinstance(exc, exc_class):
				error_code = code
				break

	# Create error detail
	error_detail = ErrorDetail(
		type=exc_type.__name__,
		message=str(exc),
		code=error_code,
		details=_extract_exception_details(exc)
	)

	# Format traceback
	tb_lines = format_traceback(exc)

	# Create error response
	return ErrorResponse(
		error=error_detail,
		timestamp=datetime.now(timezone.utc).isoformat(),
		request_id=get_request_id(),
		path=str(request.url.path),
		traceback=tb_lines
	)
