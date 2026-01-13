from datetime import datetime

from src.domain.app.entities.Game import Game
from src.domain.app.interfaces.IGameRepository import IGameRepository
from src.domain.app.repositories.mappers.GameMapper import GameMapper
from src.domain.base.factories.PydanticEntityFactory import PydanticEntityFactory
from src.domain.base.repositories.CrudRepository import CrudRepository


class GameRepository(CrudRepository[Game, GameMapper], IGameRepository):

	def _entity_to_mapper(self, entity: Game) -> GameMapper:
		"""
		Convert Game entity to GameMapper

		:param entity:
			Game entity to convert
		:return:
			GameMapper instance
		"""
		return GameMapper(
			name=entity.name,
			path=entity.path,
			last_scan_time=entity.last_scan_time,
			sessions=entity.sessions,
			saves_pattern=entity.saves_pattern
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Game"

	def _get_duplicate_identifier(self, entity: Game) -> str:
		"""
		Get duplicate identifier for Game

		:param entity:
			Game entity
		:return:
			Identifier string
		"""
		return f"path={entity.path}"

	def create(self, game: Game) -> Game:
		"""
		Create new game

		:param game:
			Game entity to create
		:return:
			Created game with database ID
		"""
		return self._create_single(game)

	def get_by_id(self, game_id: int) -> Game | None:
		with self._session_factory() as session:
			mapper = session.query(GameMapper).filter(
				GameMapper.id == game_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_path(self, path: str) -> Game | None:
		with self._session_factory() as session:
			mapper = session.query(GameMapper).filter(
				GameMapper.path == path
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[Game]:
		with self._session_factory() as session:
			mappers = session.query(GameMapper).order_by(
				GameMapper.name.asc()
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def delete(self, game_id: int) -> None:
		"""
		Delete game by ID

		:param game_id:
			Game ID to delete
		:return:
		"""
		with self._session_factory() as session:
			session.query(GameMapper).filter(
				GameMapper.id == game_id
			).delete()
			session.commit()

	def update_last_scan_time(
		self,
		game_id: int,
		scan_time: datetime
	) -> None:
		"""
		Update last scan time for a game

		:param game_id:
			Game ID to update
		:param scan_time:
			Timestamp of the scan
		:return:
		"""
		with self._session_factory() as session:
			session.query(GameMapper).filter(
				GameMapper.id == game_id
			).update({"last_scan_time": scan_time})
			session.commit()

	def _mapper_to_entity(self, mapper: GameMapper) -> Game:
		return PydanticEntityFactory.create_entity(
			Game, mapper
		)
