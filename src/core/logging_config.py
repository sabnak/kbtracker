import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
	"""
	Custom JSON formatter for structured logging

	Formats log records as JSON with structured fields including timestamp,
	level, logger name, message, and exception information.
	"""

	def format(self, record: logging.LogRecord) -> str:
		"""
		Format log record as JSON string

		:param record:
			Log record to format
		:return:
			JSON-formatted log string
		"""
		log_data: dict[str, Any] = {
			"timestamp": datetime.fromtimestamp(
				record.created,
				tz=timezone.utc
			).strftime("%Y-%m-%dT%H:%M:%S"),
			"level": record.levelname,
			"message": record.getMessage(),
		}

		# Add request ID if available (will be set by middleware)
		if hasattr(record, "request_id"):
			log_data["request_id"] = record.request_id

		# Add exception information if present
		if record.exc_info:
			log_data["exc_info"] = {
				"type": record.exc_info[0].__name__ if record.exc_info[0] else None,
				"message": str(record.exc_info[1]) if record.exc_info[1] else None,
				"traceback": traceback.format_exception(*record.exc_info)
			}

		# Add extra fields from the record
		if hasattr(record, "extra"):
			log_data["extra"] = record.extra

		return json.dumps(log_data)


def setup_logging() -> logging.Logger:
	"""
	Configure application logging with JSON formatter

	Sets up:
	- Root logger with INFO level
	- Console handler with JSON formatting
	- Uvicorn access and error loggers with JSON formatting
	"""
	# Get root logger
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.INFO)

	# Remove existing handlers to avoid duplicates
	root_logger.handlers.clear()

	# Create console handler with JSON formatter
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setLevel(logging.INFO)
	console_handler.setFormatter(JsonFormatter())

	# Add handler to root logger
	root_logger.addHandler(console_handler)

	# Configure uvicorn loggers to use JSON format
	uvicorn_access = logging.getLogger("uvicorn.access")
	uvicorn_access.handlers.clear()
	uvicorn_access.addHandler(console_handler)
	uvicorn_access.propagate = False

	uvicorn_error = logging.getLogger("uvicorn.error")
	uvicorn_error.handlers.clear()
	uvicorn_error.addHandler(console_handler)
	uvicorn_error.propagate = False

	# Configure application logger
	app_logger = logging.getLogger("kbtracker")
	app_logger.setLevel(logging.INFO)
	return app_logger


def get_logger(name: str) -> logging.Logger:
	"""
	Get a configured logger instance

	:param name:
		Logger name (typically __name__ from calling module)
	:return:
		Configured logger instance
	"""
	return logging.getLogger(name)
