from enum import Enum


class LocalizationType(str, Enum):
	"""
	Localization text type enumeration

	Defines valid types for localization strings extracted from game files.
	Types indicate what game content the localization text represents.
	"""

	FEATURE_HEADER = "feature_header"
	FEATURE_HINT = "feature_hint"
