from abc import ABC, abstractmethod

from src.domain.game.entities.Shop import Shop


class IShopFactory(ABC):

	@abstractmethod
	def produce(self) -> list[Shop]:
		"""
		Transform products into a flat list of shops

		:return:
			List of Shop entities
		"""
		pass

