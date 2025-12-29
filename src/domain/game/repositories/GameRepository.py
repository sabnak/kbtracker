from sqlalchemy.orm import Session

from src.domain.CrudRepository import CrudRepository
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.entities.Game import Game
from src.domain.game.repositories.mappers.GameMapper import GameMapper


class GameRepository(CrudRepository[Game, GameMapper], IGameRepository):

	def __init__(self, session: Session):
		super().__init__(session)

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
			path=entity.path
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
		mapper = self._session.query(GameMapper).filter(
			GameMapper.id == game_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def get_by_path(self, path: str) -> Game | None:
		mapper = self._session.query(GameMapper).filter(
			GameMapper.path == path
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[Game]:
		mappers = self._session.query(GameMapper).order_by(
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
		query = self._session.query(GameMapper).filter(
			GameMapper.id == game_id
		)
		self._delete_by_query(query)

	def _mapper_to_entity(self, mapper: GameMapper) -> Game:
		return Game(
			id=mapper.id,
			name=mapper.name,
			path=mapper.path
		)
