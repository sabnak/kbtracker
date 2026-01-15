from sqlalchemy import Column, Integer, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from src.domain.base.repositories.mappers.base import Base
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.entities.ShopType import ShopType


class ShopInventoryMapper(Base):
	__tablename__ = "shop_inventory"

	product_id = Column(Integer, primary_key=True)
	product_type = Column(Enum(ShopProductType), primary_key=True, nullable=False)
	count = Column(Integer, nullable=False, default=1)
	shop_id = Column(Integer, primary_key=True, nullable=True)
	shop_type = Column(Enum(ShopType), primary_key=True, nullable=False)
	location = Column(String(255), primary_key=True)
	profile_id = Column(Integer, ForeignKey("profile.id"), primary_key=True)

	profile = relationship("ProfileMapper", back_populates="shop_inventory")
