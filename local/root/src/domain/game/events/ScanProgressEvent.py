from dataclasses import dataclass
from typing import Any

from src.domain.game.events.ResourceType import ResourceType
from src.domain.game.events.ScanEventType import ScanEventType


@dataclass
class ScanProgressEvent:
	"""
	Event representing scan progress state

	:param event_type:
		Type of scan event
	:param resource_type:
		Type of resource being processed (None for scan-level events)
	:param count:
		Number of items processed (for completed events)
	:param message:
		Human-readable message
	:param error:
		Error message (only for error events)
	:param error_type:
		Type of error (exception class name)
	:param error_traceback:
		Full error traceback for debugging
	"""
	event_type: ScanEventType
	resource_type: ResourceType | None = None
	count: int | None = None
	message: str = ""
	error: str | None = None
	error_type: str | None = None
	error_traceback: str | None = None

	def to_dict(self) -> dict[str, Any]:
		"""
		Convert event to dictionary for JSON serialization

		:return:
			Dictionary representation
		"""
		return {
			"event_type": self.event_type.value,
			"resource_type": self.resource_type.value if self.resource_type else None,
			"count": self.count,
			"message": self.message,
			"error": self.error,
			"error_type": self.error_type,
			"error_traceback": self.error_traceback
		}
