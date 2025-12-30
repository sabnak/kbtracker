from enum import Enum


class ScanEventType(Enum):
	"""
	Event types emitted during scan operation
	"""
	SCAN_STARTED = "scan_started"
	RESOURCE_STARTED = "resource_started"
	RESOURCE_COMPLETED = "resource_completed"
	SCAN_COMPLETED = "scan_completed"
	SCAN_ERROR = "scan_error"
