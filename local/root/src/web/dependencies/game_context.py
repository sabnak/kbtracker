from fastapi import Depends, Path
from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.app.interfaces.ISchemaManagementService import ISchemaManagementService


class GameContext:
	"""
	Game context containing game ID and schema name
	"""

	def __init__(self, game_id: int, schema_name: str):
		self.game_id = game_id
		self.schema_name = schema_name


@inject
def get_game_context(
	game_id: int = Path(...),
	schema_mgmt: ISchemaManagementService = Depends(Provide[Container.schema_management_service])
) -> GameContext:
	"""
	Extract game context from URL path parameter

	:param game_id:
		Game ID from URL path
	:param schema_mgmt:
		Schema management service
	:return:
		Game context with game ID and schema name
	"""
	schema_name = schema_mgmt.get_schema_name(game_id)
	return GameContext(game_id, schema_name)
