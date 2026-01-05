from dataclasses import dataclass

from src.domain.game.entities.ShopInventoryType import ShopInventoryType


@dataclass
class ShopInventory:
	entity_id: int
	atom_map_id: int
	profile_id: int
	type: ShopInventoryType
	count: int
