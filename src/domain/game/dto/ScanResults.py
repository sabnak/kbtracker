from dataclasses import dataclass


@dataclass
class ScanResults:
	items: int
	atoms: int
	sets: int
	localizations: int
	spells: int
	units: int
