import uuid
from contextvars import ContextVar
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


_request_context: ContextVar[dict[str, str]] = ContextVar("request_context", default={})


class RequestContextMiddleware(BaseHTTPMiddleware):
	"""
	Middleware to generate and track unique request IDs

	Generates a UUID for each request and stores it in a context variable
	for use in logging and error responses. Also adds the request ID to
	response headers.
	"""

	async def dispatch(
		self,
		request: Request,
		call_next: Callable
	) -> Response:
		"""
		Process request and add request ID

		:param request:
			Incoming HTTP request
		:param call_next:
			Next middleware or route handler in chain
		:return:
			HTTP response with X-Request-ID header
		"""
		# Generate unique request ID
		request_id = str(uuid.uuid4())

		# Store in context variable for access in handlers and loggers
		_request_context.set({"request_id": request_id})

		# Process request
		response = await call_next(request)

		# Add request ID to response headers
		response.headers["X-Request-ID"] = request_id

		return response


def get_request_id() -> str:
	"""
	Get the current request ID from context

	:return:
		Current request ID, or empty string if not set
	"""
	context = _request_context.get({})
	return context.get("request_id", "")
