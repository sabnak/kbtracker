from pydantic import BaseModel


class UnitFilterDto(BaseModel):
	profile_id: int | None = None
	min_cost: int | None = None
	max_cost: int | None = None
	min_attack: int | None = None
	min_krit: int | None = None
	min_hitpoint: int | None = None
	min_defense: int | None = None
	min_speed: int | None = None
	min_initiative: int | None = None
	min_resistance_fire: int | None = None
	min_resistance_magic: int | None = None
	min_resistance_poison: int | None = None
	min_resistance_glacial: int | None = None
	min_resistance_physical: int | None = None
	min_resistance_astral: int | None = None
	level: int | None = None
