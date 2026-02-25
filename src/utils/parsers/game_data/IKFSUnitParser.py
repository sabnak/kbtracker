import abc


class IKFSUnitParser(abc.ABC):

	@abc.abstractmethod
	def parse(
		self,
		game_id: int,
		allowed_kb_ids: list[str] | None = None
	) -> dict[str, dict[str, any]]:
		"""
		Extract and parse unit data from game files

		Returns dictionary with structure: {kb_id: {kb_id, unit_class, main, params}}
		Where params contains raw arena_params data (features_hints as list, etc.)

		:param game_id:
			Game ID
		:param allowed_kb_ids:
			Optional list of unit kb_ids to parse (for testing)
			If None, parses all units found in localization
		:return:
			Dictionary mapping kb_id to raw unit data
		:raises FileNotFoundError:
			When unit atom file not found
		"""
		...
