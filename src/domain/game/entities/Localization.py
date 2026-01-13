from src.domain.base.entities.BaseEntity import BaseEntity


class Localization(BaseEntity):
	kb_id: str
	text: str
	source: str | None
	tag: str | None = None
