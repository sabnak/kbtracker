import traceback
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException, RequestValidationError

from src.core.logging_config import get_logger
from src.domain.exceptions import (
	KBTrackerException,
	DuplicateEntityException,
	EntityNotFoundException,
	DatabaseOperationException
)
from src.web.api.error_responses import (
	create_error_response,
	STATUS_CODE_MAPPING
)


templates = Jinja2Templates(directory="src/web/templates")
logger = get_logger(__name__)


def is_api_request(request: Request) -> bool:
	"""
	Determine if request expects JSON response

	Uses content negotiation to detect API requests:
	1. Path prefix: /api/* → JSON
	2. Accept header: application/json → JSON
	3. Content-Type: application/json → JSON
	4. Default: HTML

	:param request:
		FastAPI request object
	:return:
		True if request expects JSON, False for HTML
	"""
	# Check path prefix
	if request.url.path.startswith("/api/"):
		return True

	# Check Accept header
	accept = request.headers.get("accept", "")
	if "application/json" in accept:
		return True

	# Check Content-Type header
	content_type = request.headers.get("content-type", "")
	if "application/json" in content_type:
		return True

	return False


def _create_html_error_response(
	request: Request,
	error_title: str,
	error_message: str,
	error_details: str,
	status_code: int,
	error_traceback: str | None = None
) -> HTMLResponse:
	"""
	Create HTML error page response

	:param request:
		FastAPI request object
	:param error_title:
		Error title for display
	:param error_message:
		Main error message
	:param error_details:
		Detailed error explanation
	:param status_code:
		HTTP status code
	:param error_traceback:
		Optional traceback for display
	:return:
		HTML error page response
	"""
	return templates.TemplateResponse(
		"pages/error.html",
		{
			"request": request,
			"error_title": error_title,
			"error_message": error_message,
			"error_details": error_details,
			"error_traceback": error_traceback,
			"back_url": request.headers.get("referer", "/")
		},
		status_code=status_code
	)


async def kbtracker_exception_handler(
	request: Request,
	exc: KBTrackerException
) -> JSONResponse | HTMLResponse:
	"""
	Handle all KBTracker custom exceptions

	Routes to JSON or HTML response based on request type.
	Logs only unexpected exceptions (DatabaseOperationException).

	:param request:
		FastAPI request object
	:param exc:
		KBTrackerException instance
	:return:
		JSON or HTML error response
	"""
	# Log only unexpected database errors
	if isinstance(exc, DatabaseOperationException):
		logger.error(
			f"Database error: {exc.message}",
			exc_info=exc,
			extra={"path": request.url.path, "operation": exc.operation}
		)

	# Determine response format
	if is_api_request(request):
		# JSON response for API
		error_response = create_error_response(request, exc)
		status_code = STATUS_CODE_MAPPING.get(type(exc), 500)

		return JSONResponse(
			status_code=status_code,
			content=error_response.to_dict()
		)
	else:
		# HTML response for web routes
		# Generate error details based on exception type
		if isinstance(exc, DuplicateEntityException):
			error_title = "Duplicate Entity"
			error_details = (
				f"A {exc.entity_type} with the identifier "
				f"'{exc.identifier}' already exists in the database. "
				f"This might mean the data has already been imported."
			)
			status_code = 409

		elif isinstance(exc, EntityNotFoundException):
			error_title = "Not Found"
			error_details = (
				f"The {exc.entity_type} you're looking for "
				f"doesn't exist or has been deleted."
			)
			status_code = 404

		elif isinstance(exc, DatabaseOperationException):
			error_title = "Database Error"
			error_details = (
				"A database error occurred. "
				"Please try again or contact support if the problem persists."
			)
			status_code = 500

		else:
			# Generic KB Tracker exception
			error_title = type(exc).__name__
			error_details = exc.message
			status_code = STATUS_CODE_MAPPING.get(type(exc), 500)

		# Format traceback for HTML display
		tb_formatted = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

		return _create_html_error_response(
			request=request,
			error_title=error_title,
			error_message=exc.message,
			error_details=error_details,
			status_code=status_code,
			error_traceback=tb_formatted
		)


async def http_exception_handler(
	request: Request,
	exc: HTTPException
) -> JSONResponse | HTMLResponse:
	"""
	Handle FastAPI HTTPException

	Routes to JSON or HTML response based on request type.
	Does not log as these are expected HTTP errors.

	:param request:
		FastAPI request object
	:param exc:
		HTTPException instance
	:return:
		JSON or HTML error response
	"""
	# Determine response format
	if is_api_request(request):
		# JSON response for API
		error_response = create_error_response(request, exc)

		return JSONResponse(
			status_code=exc.status_code,
			content=error_response.to_dict()
		)
	else:
		# HTML response for web routes
		error_title = f"HTTP {exc.status_code}"
		error_message = str(exc.detail)
		error_details = f"The server returned a {exc.status_code} status code."

		# Format traceback for HTML display
		tb_formatted = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

		return _create_html_error_response(
			request=request,
			error_title=error_title,
			error_message=error_message,
			error_details=error_details,
			status_code=exc.status_code,
			error_traceback=tb_formatted
		)


async def validation_error_handler(
	request: Request,
	exc: RequestValidationError
) -> JSONResponse | HTMLResponse:
	"""
	Handle Pydantic validation errors

	Routes to JSON or HTML response based on request type.
	Does not log as these are expected validation errors.

	:param request:
		FastAPI request object
	:param exc:
		RequestValidationError instance
	:return:
		JSON or HTML error response
	"""
	# Determine response format
	if is_api_request(request):
		# JSON response for API
		error_response = create_error_response(request, exc)

		return JSONResponse(
			status_code=422,
			content=error_response.to_dict()
		)
	else:
		# HTML response for web routes
		error_title = "Validation Error"
		error_message = "The request contains invalid data"
		error_details = "Please check your input and try again."

		# Format traceback for HTML display
		tb_formatted = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

		return _create_html_error_response(
			request=request,
			error_title=error_title,
			error_message=error_message,
			error_details=error_details,
			status_code=422,
			error_traceback=tb_formatted
		)


async def generic_exception_handler(
	request: Request,
	exc: Exception
) -> JSONResponse | HTMLResponse:
	"""
	Handle unexpected exceptions

	Catch-all handler for any unhandled exceptions.
	Always logs these as they represent unexpected errors.

	:param request:
		FastAPI request object
	:param exc:
		Exception instance
	:return:
		JSON or HTML error response
	"""
	# Log unexpected exception
	logger.error(
		f"Unhandled exception: {exc}",
		exc_info=exc,
		extra={
			"path": request.url.path,
			"method": request.method
		}
	)

	# Determine response format
	if is_api_request(request):
		# JSON response for API
		error_response = create_error_response(request, exc)

		return JSONResponse(
			status_code=500,
			content=error_response.to_dict()
		)
	else:
		# HTML response for web routes
		error_title = "Internal Server Error"
		error_message = str(exc)
		error_details = (
			"An unexpected error occurred. "
			"Please try again or contact support if the problem persists."
		)

		# Format traceback for HTML display
		tb_formatted = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

		return _create_html_error_response(
			request=request,
			error_title=error_title,
			error_message=error_message,
			error_details=error_details,
			status_code=500,
			error_traceback=tb_formatted
		)


# Legacy handler exports for backward compatibility (if needed)
duplicate_entity_exception_handler = kbtracker_exception_handler
entity_not_found_exception_handler = kbtracker_exception_handler
database_operation_exception_handler = kbtracker_exception_handler
