from enum import Enum


class ShopInventoryType(Enum):
	"""
	Types of shop inventory entities
	"""
	GARRISON = "garrison"
	ITEM = "item"
	SPELL = "spell"
	UNIT = "unit"
