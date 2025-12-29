from dataclasses import dataclass


@dataclass
class ShopHasItem:
	item_id: int
	shop_id: int
	profile_id: int
	count: int
