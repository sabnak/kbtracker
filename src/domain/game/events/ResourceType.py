from enum import Enum


class ResourceType(Enum):
	"""
	Types of resources scanned
	"""
	LOCALIZATIONS = "localizations"
	ITEMS = "items"
	SETS = "sets"
	ATOMS = "atoms"
	ACTORS = "actors"
	SPELLS = "spells"
	UNITS = "units"
