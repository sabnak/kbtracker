import abc
import typing

from src.domain.game.dto.ShopsGroupBy import ShopsGroupBy
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopProductType import ShopProductType


class IShopInventoryService(abc.ABC):

	@abc.abstractmethod
	def get_shops_by_location(
		self,
		profile_id: int,
		group_by: ShopsGroupBy = ShopsGroupBy.LOCATION,
		types: typing.Iterable[ShopProductType] = None
	) -> dict[str, dict[str, list[Shop]]]:
		...
