from src.domain.base.repositories.CrudRepository import CrudRepository
from src.domain.game.entities.ShopProduct import ShopProduct
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.repositories.mappers.ShopInventoryMapper import ShopInventoryMapper


class ShopInventoryRepository(CrudRepository[ShopProduct, ShopInventoryMapper], IShopInventoryRepository):

	def _entity_to_mapper(self, entity: ShopProduct) -> ShopInventoryMapper:
		"""
		Convert ShopProduct entity to ShopInventoryMapper

		:param entity:
			ShopProduct entity to convert
		:return:
			ShopInventoryMapper instance
		"""
		return ShopInventoryMapper(
			entity_id=entity.entity_id,
			type=entity.type,
			atom_map_id=entity.atom_map_id,
			profile_id=entity.profile_id,
			count=entity.count
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "ShopProduct"

	def _get_duplicate_identifier(self, entity: ShopProduct) -> str:
		"""
		Get duplicate identifier for ShopProduct

		:param entity:
			ShopProduct entity
		:return:
			Identifier string
		"""
		return f"entity_id={entity.entity_id}, type={entity.type.value}, atom_map_id={entity.atom_map_id}, profile_id={entity.profile_id}"

	def create(self, inventory: ShopProduct) -> ShopProduct:
		"""
		Create new shop inventory entry

		:param inventory:
			ShopProduct entity to create
		:return:
			Created inventory entry
		"""
		return self._create_single(inventory)

	def get_by_profile(
		self,
		profile_id: int,
		type: ShopProductType | None = None
	) -> list[ShopProduct]:
		"""
		Get all inventory entries for a profile, optionally filtered by type

		:param profile_id:
			Profile ID
		:param type:
			Optional inventory type filter
		:return:
			List of inventory entries
		"""
		with self._get_session() as session:
			query = session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.profile_id == profile_id
			)
			if type:
				query = query.filter(ShopInventoryMapper.type == type)
			mappers = query.all()
			return [self._mapper_to_entity(m) for m in mappers]

	def get_by_entity(
		self,
		entity_id: int,
		type: ShopProductType,
		profile_id: int
	) -> list[ShopProduct]:
		"""
		Get all shops where an entity is found for a profile

		:param entity_id:
			Entity ID
		:param type:
			Entity type
		:param profile_id:
			Profile ID
		:return:
			List of inventory entries
		"""
		with self._get_session() as session:
			mappers = session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.entity_id == entity_id,
				ShopInventoryMapper.type == type,
				ShopInventoryMapper.profile_id == profile_id
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def delete(
		self,
		entity_id: int,
		type: ShopProductType,
		atom_map_id: int,
		profile_id: int
	) -> None:
		"""
		Delete shop inventory entry

		:param entity_id:
			Entity ID
		:param type:
			Entity type
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:return:
		"""
		with self._get_session() as session:
			session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.entity_id == entity_id,
				ShopInventoryMapper.type == type,
				ShopInventoryMapper.atom_map_id == atom_map_id,
				ShopInventoryMapper.profile_id == profile_id
			).delete()
			session.commit()

	def delete_by_profile(self, profile_id: int) -> None:
		"""
		Delete all shop inventory entries for a profile

		:param profile_id:
			Profile ID
		:return:
		"""
		with self._get_session() as session:
			session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.profile_id == profile_id
			).delete()
			session.commit()

	def update_count(
		self,
		entity_id: int,
		type: ShopProductType,
		atom_map_id: int,
		profile_id: int,
		new_count: int
	) -> ShopProduct:
		"""
		Update count for shop inventory entry

		:param entity_id:
			Entity ID
		:param type:
			Entity type
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:param new_count:
			New count value
		:return:
			Updated inventory entry
		"""
		with self._get_session() as session:
			mapper = session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.entity_id == entity_id,
				ShopInventoryMapper.type == type,
				ShopInventoryMapper.atom_map_id == atom_map_id,
				ShopInventoryMapper.profile_id == profile_id
			).first()

			if not mapper:
				from src.domain.exceptions import EntityNotFoundException
				raise EntityNotFoundException(
					f"ShopInventory not found: entity_id={entity_id}, type={type.value}, atom_map_id={atom_map_id}, profile_id={profile_id}"
				)

			mapper.count = new_count
			session.commit()
			session.refresh(mapper)

			return self._mapper_to_entity(mapper)

	def _mapper_to_entity(self, mapper: ShopInventoryMapper) -> ShopProduct:
		"""
		Convert ShopInventoryMapper to ShopProduct entity

		:param mapper:
			ShopInventoryMapper instance to convert
		:return:
			ShopProduct entity
		"""
		return ShopProduct(
			entity_id=mapper.entity_id,
			type=mapper.type,
			atom_map_id=mapper.atom_map_id,
			profile_id=mapper.profile_id,
			count=mapper.count
		)
