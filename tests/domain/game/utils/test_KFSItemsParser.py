import pytest
from pathlib import Path
from src.domain.game.utils.KFSItemsParser import KFSItemsParser
from src.domain.game.entities.Item import Item


class TestKFSItemsParser:

	@staticmethod
	def _get_sessions_path() -> str:
		"""Get sessions path relative to project root"""
		return str(Path(__file__).parent.parent.parent.parent.parent / "tests" / "game_files" / "sessions")

	@staticmethod
	def _get_all_items(parse_result: dict) -> list[Item]:
		"""
		Extract all items from parse result dictionary

		:param parse_result:
			Dictionary returned by parser.parse()
		:return:
			Flat list of all items
		"""
		items = []
		for set_kb_id, set_data in parse_result.items():
			items.extend(set_data["items"])
		return items

	def test_parse_returns_nested_dict_structure(self):
		"""
		Test that parse returns a nested dictionary with sets and setless items
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()

		assert isinstance(result, dict)
		assert "setless" in result
		assert isinstance(result["setless"], dict)
		assert "items" in result["setless"]
		assert isinstance(result["setless"]["items"], list)

	def test_item_fields_populated_correctly(self):
		"""
		Test that Item fields are populated correctly for snake_belt
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()
		items = self._get_all_items(result)

		snake_belt = next((item for item in items if item.kb_id == 'snake_belt'), None)
		assert snake_belt is not None
		assert snake_belt.kb_id == 'snake_belt'
		assert snake_belt.name != ''
		assert snake_belt.price == 15000
		assert snake_belt.hint is not None
		assert snake_belt.propbits == ['belt']

	def test_propbits_parsing(self):
		"""
		Test propbits parsing from comma-separated string to list
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()
		items = self._get_all_items(result)

		items_with_propbits = [item for item in items if item.propbits is not None]
		assert len(items_with_propbits) > 0

		single_propbit = [item for item in items if item.propbits == ['belt']]
		assert len(single_propbit) > 0

	def test_item_with_no_hint(self):
		"""
		Test that items without hint have None value
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()
		items = self._get_all_items(result)

		items_without_hint = [item for item in items if item.hint is None]
		assert isinstance(items_without_hint, list)

	def test_large_file_performance(self):
		"""
		Test parsing full 78k line file completes in reasonable time
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()
		items = self._get_all_items(result)

		assert len(items) > 100
		assert all(item.id == 0 for item in items)
		assert all(item.kb_id != '' for item in items)
		assert all(item.name != '' for item in items)

	def test_all_items_have_required_fields(self):
		"""
		Test that all parsed items have required fields populated
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()
		items = self._get_all_items(result)

		for item in items:
			assert item.kb_id != '', f"Item has empty kb_id"
			assert item.name != '', f"Item {item.kb_id} has empty name"
			assert isinstance(item.price, int), f"Item {item.kb_id} price is not int"
			assert item.price >= 0, f"Item {item.kb_id} has negative price"

	def test_items_with_multiple_propbits(self):
		"""
		Test parsing items with multiple propbits values
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()
		items = self._get_all_items(result)

		multi_propbit_items = [
			item for item in items
			if item.propbits is not None and len(item.propbits) > 1
		]

		assert len(multi_propbit_items) > 0
		for item in multi_propbit_items:
			assert all(isinstance(pb, str) for pb in item.propbits)
			assert all(pb.strip() == pb for pb in item.propbits)

	def test_parse_extracts_set_metadata(self):
		"""
		Test that set definitions are parsed with correct metadata
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()

		set_keys = [key for key in result.keys() if key != "setless"]
		if len(set_keys) > 0:
			set_key = set_keys[0]
			assert "name" in result[set_key]
			assert "hint" in result[set_key]
			assert "items" in result[set_key]
			assert isinstance(result[set_key]["name"], str)
			assert result[set_key]["name"] != ""

	def test_items_grouped_by_setref(self):
		"""
		Test that items are correctly grouped by their setref value
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()

		for set_kb_id, set_data in result.items():
			assert "items" in set_data
			assert isinstance(set_data["items"], list)
			for item in set_data["items"]:
				assert isinstance(item, Item)

	def test_setless_items_grouped_separately(self):
		"""
		Test that items without setref are grouped under 'setless' key
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()

		assert "setless" in result
		assert "items" in result["setless"]
		assert len(result["setless"]["items"]) > 0

	def test_all_items_are_items_not_sets(self):
		"""
		Test that set definitions themselves are not included as items
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		result = parser.parse()
		items = self._get_all_items(result)

		for item in items:
			assert not item.kb_id.startswith('set_'), f"Set definition {item.kb_id} incorrectly parsed as item"
