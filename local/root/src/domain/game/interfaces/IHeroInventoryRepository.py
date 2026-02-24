from abc import ABC, abstractmethod

from src.domain.game.entities.HeroInventoryProduct import HeroInventoryProduct
from src.domain.game.entities.InventoryEntityType import InventoryEntityType


class IHeroInventoryRepository(ABC):

	@abstractmethod
	def create(self, inventory: HeroInventoryProduct) -> HeroInventoryProduct:
		pass

	@abstractmethod
	def get_by_profile(
		self,
		profile_id: int,
		product_types: list[InventoryEntityType] | None = None
	) -> list[HeroInventoryProduct]:
		pass

	@abstractmethod
	def delete_by_profile(self, profile_id: int) -> None:
		pass
