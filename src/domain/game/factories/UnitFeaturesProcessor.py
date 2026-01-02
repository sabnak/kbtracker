from src.domain.game.ILocalizationRepository import ILocalizationRepository


class UnitFeaturesProcessor:

	def __init__(self, localization_repository: ILocalizationRepository):
		"""
		Initialize features processor

		:param localization_repository:
			Repository for fetching localized text
		"""
		self._localization_repository = localization_repository

	def process(self, params: dict) -> dict[str, dict[str, str]] | None:
		"""
		Process features from params.features_hints with localization

		features_hints format: ["header_kb_id/hint_kb_id", ...]
		Returns: {"full_kb_id": {name, hint}, ...}

		:param params:
			Unit params dictionary
		:return:
			Processed features or None if no features_hints
		"""
		features_hints = params.get('features_hints')
		if not features_hints:
			return None

		result = {}

		for full_kb_id in features_hints:
			parts = full_kb_id.split('/')
			if len(parts) != 2:
				continue

			name_kb_id, hint_kb_id = parts

			name_loc = self._localization_repository.get_by_kb_id(name_kb_id)
			hint_loc = self._localization_repository.get_by_kb_id(hint_kb_id)

			name_text = name_loc.text if name_loc else name_kb_id
			hint_text = hint_loc.text if hint_loc else hint_kb_id

			result[full_kb_id] = {
				'name': name_text,
				'hint': hint_text
			}

		return result if result else None
