from src.domain.game.ILocalizationRepository import ILocalizationRepository


class UnitAttacksProcessor:

	def __init__(self, localization_repository: ILocalizationRepository):
		"""
		Initialize attacks processor

		:param localization_repository:
			Repository for fetching localized text
		"""
		self._localization_repository = localization_repository

	def process(self, params: dict) -> dict[str, dict[str, any]] | None:
		"""
		Process attacks from params with localization

		Searches for attack dictionaries that contain 'hint' key.
		For each: fetches hint text, derives name kb_id, fetches name text.

		:param params:
			Unit params dictionary
		:return:
			Processed attacks or None if no special attacks found
		"""
		result = {}

		for key, value in params.items():
			if not isinstance(value, dict):
				continue

			hint_kb_id = value.get('hint')
			if not hint_kb_id:
				continue

			hint_loc = self._localization_repository.get_by_kb_id(hint_kb_id)
			hint_text = hint_loc.text if hint_loc else hint_kb_id

			name_kb_id = hint_kb_id.replace('_hint', '_name')

			name_loc = self._localization_repository.get_by_kb_id(name_kb_id)
			name_text = name_loc.text if name_loc else name_kb_id

			result[key] = {
				'name': name_text,
				'hint': hint_text,
				'data': value
			}

		return result if result else None
