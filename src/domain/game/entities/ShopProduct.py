from dataclasses import dataclass

from src.domain.game.entities.ShopProductType import ShopProductType


@dataclass
class ShopProduct:
	entity_id: int
	atom_map_id: int
	profile_id: int
	type: ShopProductType
	count: int
