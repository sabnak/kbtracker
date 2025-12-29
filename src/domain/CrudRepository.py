from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.domain.exceptions import (
	DuplicateEntityException,
	DatabaseOperationException
)


TEntity = TypeVar("TEntity")
TMapper = TypeVar("TMapper")


class CrudRepository(ABC, Generic[TEntity, TMapper]):
	"""
	Base CRUD repository with common error handling
	"""

	def __init__(self, session: Session):
		self._session = session

	@abstractmethod
	def _entity_to_mapper(self, entity: TEntity) -> TMapper:
		"""
		Convert entity to mapper

		:param entity:
			Entity to convert
		:return:
			Mapper instance
		"""
		pass

	@abstractmethod
	def _mapper_to_entity(self, mapper: TMapper) -> TEntity:
		"""
		Convert mapper to entity

		:param mapper:
			Mapper to convert
		:return:
			Entity instance
		"""
		pass

	@abstractmethod
	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name for error messages

		:return:
			Entity type name (e.g., "Item", "Game")
		"""
		pass

	@abstractmethod
	def _get_duplicate_identifier(self, entity: TEntity) -> str:
		"""
		Get identifier string for duplicate error messages

		:param entity:
			Entity that caused duplicate error
		:return:
			Identifier string (e.g., "game_id=1, kb_id=sword")
		"""
		pass

	def _create_single(self, entity: TEntity) -> TEntity:
		"""
		Create single entity with error handling

		:param entity:
			Entity to create
		:return:
			Created entity with database ID
		:raises DuplicateEntityException:
			When entity with unique constraint already exists
		:raises DatabaseOperationException:
			When database operation fails
		"""
		mapper = self._entity_to_mapper(entity)

		try:
			self._session.add(mapper)
			self._session.commit()
			self._session.refresh(mapper)
			return self._mapper_to_entity(mapper)
		except IntegrityError as e:
			self._session.rollback()
			error_msg = str(e.orig)
			if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
				raise DuplicateEntityException(
					entity_type=self._get_entity_type_name(),
					identifier=self._get_duplicate_identifier(entity),
					original_exception=e
				)
			raise DatabaseOperationException(
				operation=f"create {self._get_entity_type_name()}",
				details=error_msg,
				original_exception=e
			)
		except SQLAlchemyError as e:
			self._session.rollback()
			raise DatabaseOperationException(
				operation=f"create {self._get_entity_type_name()}",
				details=str(e),
				original_exception=e
			)

	def _create_batch(self, entities: list[TEntity]) -> list[TEntity]:
		"""
		Create multiple entities in a batch with error handling

		:param entities:
			List of entities to create
		:return:
			List of created entities with database IDs
		:raises DuplicateEntityException:
			When any entity with unique constraint already exists
		:raises DatabaseOperationException:
			When database operation fails
		"""
		mappers = [self._entity_to_mapper(entity) for entity in entities]

		try:
			self._session.add_all(mappers)
			self._session.commit()
			for mapper in mappers:
				self._session.refresh(mapper)
			return [self._mapper_to_entity(m) for m in mappers]
		except IntegrityError as e:
			self._session.rollback()
			error_msg = str(e.orig)
			if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
				raise DuplicateEntityException(
					entity_type=f"{self._get_entity_type_name()} batch",
					identifier=f"{len(entities)} items",
					original_exception=e
				)
			raise DatabaseOperationException(
				operation=f"batch create {self._get_entity_type_name()}",
				details=error_msg,
				original_exception=e
			)
		except SQLAlchemyError as e:
			self._session.rollback()
			raise DatabaseOperationException(
				operation=f"batch create {self._get_entity_type_name()}",
				details=str(e),
				original_exception=e
			)

	def _delete_by_query(self, query) -> None:
		"""
		Delete entities by query with error handling

		:param query:
			SQLAlchemy query to delete
		:return:
		:raises DatabaseOperationException:
			When database operation fails
		"""
		try:
			query.delete()
			self._session.commit()
		except IntegrityError as e:
			self._session.rollback()
			error_msg = str(e.orig)
			if "foreign key" in error_msg.lower():
				raise DatabaseOperationException(
					operation=f"delete {self._get_entity_type_name()}",
					details="Cannot delete: entity is referenced by other records",
					original_exception=e
				)
			raise DatabaseOperationException(
				operation=f"delete {self._get_entity_type_name()}",
				details=error_msg,
				original_exception=e
			)
		except SQLAlchemyError as e:
			self._session.rollback()
			raise DatabaseOperationException(
				operation=f"delete {self._get_entity_type_name()}",
				details=str(e),
				original_exception=e
			)
