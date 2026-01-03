from dataclasses import dataclass


@dataclass
class LocEntity:

	name: str | None = None
	hint: str | None = None
	desc: str | None = None
	header: str | None = None
	texts: dict[str, str] | None = None
