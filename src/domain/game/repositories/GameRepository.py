from sqlalchemy.orm import Session

from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.entities.Game import Game
from src.domain.game.repositories.mappers.GameMapper import GameMapper


class GameRepository(IGameRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, game: Game) -> Game:
		mapper = GameMapper(
			name=game.name,
			path=game.path
		)
		self._session.add(mapper)
		self._session.commit()
		self._session.refresh(mapper)
		return self._mapper_to_entity(mapper)

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
		self._session.query(GameMapper).filter(
			GameMapper.id == game_id
		).delete()
		self._session.commit()

	@staticmethod
	def _mapper_to_entity(mapper: GameMapper) -> Game:
		return Game(
			id=mapper.id,
			name=mapper.name,
			path=mapper.path
		)
