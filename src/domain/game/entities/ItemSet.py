from src.domain.base.entities.BaseEntity import BaseEntity


class ItemSet(BaseEntity):
	id: int
	kb_id: str
	name: str | None = None
	hint: str | None = None
