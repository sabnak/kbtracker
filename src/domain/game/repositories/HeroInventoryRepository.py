from src.domain.base.factories.PydanticEntityFactory import PydanticEntityFactory
from src.domain.base.repositories.CrudRepository import CrudRepository
from src.domain.game.entities.HeroInventoryProduct import HeroInventoryProduct
from src.domain.game.entities.InventoryEntityType import InventoryEntityType
from src.domain.game.interfaces.IHeroInventoryRepository import IHeroInventoryRepository
from src.domain.game.repositories.mappers.HeroInventoryMapper import HeroInventoryMapper


class HeroInventoryRepository(
	CrudRepository[HeroInventoryProduct, HeroInventoryMapper],
	IHeroInventoryRepository
):

	def create(self, inventory: HeroInventoryProduct) -> HeroInventoryProduct:
		return self._create_single(inventory)

	def get_by_profile(
		self,
		profile_id: int,
		product_types: list[InventoryEntityType] | None = None
	) -> list[HeroInventoryProduct]:
		with self._get_session() as session:
			query = session.query(HeroInventoryMapper).filter(
				HeroInventoryMapper.profile_id == profile_id
			)

			if product_types is not None:
				query = query.filter(HeroInventoryMapper.product_type.in_(product_types))

			mappers = query.all()
			return [self._mapper_to_entity(mapper) for mapper in mappers]

	def delete_by_profile(self, profile_id: int) -> None:
		with self._get_session() as session:
			session.query(HeroInventoryMapper).filter(
				HeroInventoryMapper.profile_id == profile_id
			).delete(synchronize_session=False)

	def _entity_to_mapper(self, entity: HeroInventoryProduct) -> HeroInventoryMapper:
		return HeroInventoryMapper(
			product_id=entity.product_id,
			product_type=entity.product_type,
			count=entity.count,
			profile_id=entity.profile_id
		)

	def _mapper_to_entity(self, mapper: HeroInventoryMapper) -> HeroInventoryProduct:
		return PydanticEntityFactory.create_entity(HeroInventoryProduct, mapper)

	def _get_entity_type_name(self) -> str:
		return "HeroInventoryProduct"

	def _get_duplicate_identifier(self, entity: HeroInventoryProduct) -> str:
		return f"profile_id={entity.profile_id}, product_id={entity.product_id}, product_type={entity.product_type}"
