from dataclasses import dataclass


@dataclass
class ObjectHasItem:
	item_id: int
	object_id: int
	profile_id: int
	count: int
