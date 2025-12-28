import pytest
from pathlib import Path
from src.domain.game.utils.KFSItemsParser import KFSItemsParser
from src.domain.game.entities.Item import Item


class TestKFSItemsParser:

	@staticmethod
	def _get_sessions_path() -> str:
		"""Get sessions path relative to project root"""
		return str(Path(__file__).parent.parent.parent.parent.parent / "tests" / "game_files" / "sessions")

	def test_parse_returns_item_list(self):
		"""
		Test that parse returns a list of Item objects
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		items = parser.parse()

		assert isinstance(items, list)
		assert len(items) > 0
		assert all(isinstance(item, Item) for item in items)

	def test_item_fields_populated_correctly(self):
		"""
		Test that Item fields are populated correctly for snake_belt
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		items = parser.parse()

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

		items = parser.parse()

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

		items = parser.parse()

		items_without_hint = [item for item in items if item.hint is None]
		assert isinstance(items_without_hint, list)

	def test_large_file_performance(self):
		"""
		Test parsing full 78k line file completes in reasonable time
		"""
		sessions_path = self._get_sessions_path()
		parser = KFSItemsParser(sessions_path)

		items = parser.parse()

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

		items = parser.parse()

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

		items = parser.parse()

		multi_propbit_items = [
			item for item in items
			if item.propbits is not None and len(item.propbits) > 1
		]

		assert len(multi_propbit_items) > 0
		for item in multi_propbit_items:
			assert all(isinstance(pb, str) for pb in item.propbits)
			assert all(pb.strip() == pb for pb in item.propbits)
