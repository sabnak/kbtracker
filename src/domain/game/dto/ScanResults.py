from dataclasses import dataclass


@dataclass
class ScanResults:
	items: int
	locations: int
	shops: int
	sets: int
