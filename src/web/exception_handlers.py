from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.domain.exceptions import (
	DuplicateEntityException,
	EntityNotFoundException,
	DatabaseOperationException
)


templates = Jinja2Templates(directory="src/web/templates")


async def duplicate_entity_exception_handler(
	request: Request,
	exc: DuplicateEntityException
) -> HTMLResponse:
	"""
	Handle duplicate entity exceptions

	:param request:
		FastAPI request object
	:param exc:
		DuplicateEntityException instance
	:return:
		HTML error page
	"""
	return templates.TemplateResponse(
		"pages/error.html",
		{
			"request": request,
			"error_title": "Duplicate Entity",
			"error_message": exc.message,
			"error_details": (
				f"A {exc.entity_type} with the identifier "
				f"'{exc.identifier}' already exists in the database. "
				f"This might mean the data has already been imported."
			),
			"back_url": request.headers.get("referer", "/")
		},
		status_code=409
	)


async def entity_not_found_exception_handler(
	request: Request,
	exc: EntityNotFoundException
) -> HTMLResponse:
	"""
	Handle entity not found exceptions

	:param request:
		FastAPI request object
	:param exc:
		EntityNotFoundException instance
	:return:
		HTML error page
	"""
	return templates.TemplateResponse(
		"pages/error.html",
		{
			"request": request,
			"error_title": "Not Found",
			"error_message": exc.message,
			"error_details": (
				f"The {exc.entity_type} you're looking for "
				f"doesn't exist or has been deleted."
			),
			"back_url": request.headers.get("referer", "/")
		},
		status_code=404
	)


async def database_operation_exception_handler(
	request: Request,
	exc: DatabaseOperationException
) -> HTMLResponse:
	"""
	Handle database operation exceptions

	:param request:
		FastAPI request object
	:param exc:
		DatabaseOperationException instance
	:return:
		HTML error page
	"""
	return templates.TemplateResponse(
		"pages/error.html",
		{
			"request": request,
			"error_title": "Database Error",
			"error_message": f"Failed to {exc.operation}",
			"error_details": (
				"A database error occurred. "
				"Please try again or contact support if the problem persists."
			),
			"back_url": request.headers.get("referer", "/")
		},
		status_code=500
	)
