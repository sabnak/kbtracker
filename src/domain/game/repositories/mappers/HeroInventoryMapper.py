from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from src.domain.base.repositories.mappers.base import Base
from src.domain.game.entities.InventoryEntityType import InventoryEntityType


class HeroInventoryMapper(Base):
	__tablename__ = "hero_inventory"

	product_id = Column(Integer, primary_key=True)
	product_type = Column(Enum(InventoryEntityType), primary_key=True, nullable=False)
	count = Column(Integer, nullable=False, default=1)
	profile_id = Column(Integer, ForeignKey("profile.id"), primary_key=True)

	profile = relationship("ProfileMapper", back_populates="hero_inventory")
