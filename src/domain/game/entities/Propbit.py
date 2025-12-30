from enum import Enum


class Propbit(str, Enum):
	"""
	Item property bits enumeration

	Defines valid property flags that can be assigned to game items.
	Multiple propbits can be assigned to a single item.
	"""

	ARMOR = "armor"
	ARTEFACT = "artefact"
	BELT = "belt"
	BOOTS = "boots"
	CONTAINER = "container"
	DIALOG = "dialog"
	GLOVES = "gloves"
	HELMET = "helmet"
	HIDDEN = "hidden"
	MORAL = "moral"
	MULTIUSE = "multiuse"
	PANTS = "pants"
	QUEST = "quest"
	RARE = "rare"
	REGALIA = "regalia"
	SHIELD = "shield"
	USABLE = "usable"
	WEAPON = "weapon"
	WIFE = "wife"
	MAP = "map"
