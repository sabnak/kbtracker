from enum import Enum


class ShopProductType(Enum):
	"""
	Types of shop product entities
	"""
	GARRISON = "garrison"
	ITEM = "item"
	SPELL = "spell"
	UNIT = "unit"
