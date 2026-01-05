from dataclasses import dataclass


@dataclass
class ShopInventory:
	entity_id: int
	atom_map_id: int
	profile_id: int
	type: str
	count: int
