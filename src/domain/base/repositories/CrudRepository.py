from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import TypeVar, Generic, Optional
from dependency_injector.wiring import Provide, inject
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.Container import Container
from src.domain.exceptions import (
	DuplicateEntityException,
	DatabaseOperationException
)
from src.utils.db import create_schema_session
from src.web.dependencies.game_context import GameContext

TEntity = TypeVar("TEntity")
TMapper = TypeVar("TMapper")

# Module-level context variable for game context
GAME_CONTEXT: ContextVar[Optional['GameContext']] = ContextVar('game_context', default=None)


class CrudRepository(ABC, Generic[TEntity, TMapper]):
	"""
	Base CRUD repository with common error handling
	"""

	@inject
	def __init__(self, session_factory: sessionmaker[Session] = Provide[Container.db_session_factory]):
		self._session_factory = session_factory

	def _get_session(self):
		"""
		Get session with schema context if available

		:return:
			Session or SchemaContextSession
		"""
		context = GAME_CONTEXT.get()
		if context:
			return create_schema_session(self._session_factory, context.schema_name)
		return self._session_factory()

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

		with self._get_session() as session:
			try:
				session.add(mapper)
				session.commit()
				session.refresh(mapper)
				return self._mapper_to_entity(mapper)
			except IntegrityError as e:
				session.rollback()
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
				session.rollback()
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

		with self._get_session() as session:
			try:
				session.add_all(mappers)
				session.commit()
				for mapper in mappers:
					session.refresh(mapper)
				return [self._mapper_to_entity(m) for m in mappers]
			except IntegrityError as e:
				session.rollback()
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
				session.rollback()
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
		with self._get_session() as session:
			try:
				query.delete()
				session.commit()
			except IntegrityError as e:
				session.rollback()
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
				session.rollback()
				raise DatabaseOperationException(
					operation=f"delete {self._get_entity_type_name()}",
					details=str(e),
					original_exception=e
				)
