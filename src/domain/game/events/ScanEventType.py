from enum import Enum


class ScanEventType(Enum):
	"""
	Event types emitted during scan operation
	"""
	SCAN_STARTED = "scan_started"
	EXTRACTION_STARTED = "extraction_started"
	EXTRACTION_COMPLETED = "extraction_completed"
	EXTRACTION_WARNING = "extraction_warning"
	RESOURCE_STARTED = "resource_started"
	RESOURCE_COMPLETED = "resource_completed"
	SCAN_COMPLETED = "scan_completed"
	SCAN_ERROR = "scan_error"
