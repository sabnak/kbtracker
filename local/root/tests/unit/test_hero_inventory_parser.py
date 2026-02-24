import pytest
from pathlib import Path
from unittest.mock import Mock

from src.utils.parsers.save_data.SaveDataParser import SaveDataParser
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


@pytest.fixture
def mock_item_repository():
	"""
	Create mock ItemRepository that validates common item kb_ids

	:return:
		Mock ItemRepository instance
	"""
	mock_repo = Mock()

	# List of known valid item prefixes from the save file
	valid_item_prefixes = [
		'addon3_', 'addon4_', 'kerus_', 'flame_', 'arhmage_', 'destructor_',
		'sword_', 'wizard_', 'battlemage_', 'pictures_', 'elf_', 'human_',
		'demon_', 'neutral_', 'orc_', 'dwarf_', 'inventor_', 'undead_'
	]

	# Items to exclude (not real items)
	invalid_items = [
		'achievement_', 'medal_', 'sp_', 'slbody', 'experience', 'defense',
		'crystals', 'wife0', 'wife1', 'wife2', 'wife3', 'comp1_item',
		'comp2_item', 'comp3_item', 'comp4_item', 'hidden_', 'warrior_bonus_',
		'demoness_', 'count', 'flags', 'lvars', 'strg', 'bmd', 'id'
	]

	def is_item_exists(kb_id: str) -> bool:
		# Check if it starts with invalid prefix
		for invalid in invalid_items:
			if kb_id.startswith(invalid) or kb_id == invalid:
				return False

		# Check if it starts with valid prefix
		for prefix in valid_item_prefixes:
			if kb_id.startswith(prefix):
				return True

		return False

	mock_repo.is_item_exists.side_effect = is_item_exists

	return mock_repo


@pytest.fixture
def parser(mock_item_repository):
	"""
	Create SaveDataParser instance for testing

	:param mock_item_repository:
		Mock ItemRepository instance
	:return:
		SaveDataParser instance with real decompressor and mock repository
	"""
	decompressor = SaveFileDecompressor()
	return SaveDataParser(decompressor, mock_item_repository)


@pytest.fixture
def inventory_save_path():
	"""
	Path to test save with hero inventory

	:return:
		Path to inventory1769382036 save directory
	"""
	return Path(__file__).parent.parent / "game_files" / "saves" / "inventory1769382036"


class TestHeroInventoryParser:

	def test_parse_hero_inventory_basic(self, parser, inventory_save_path):
		"""
		Test basic hero inventory parsing

		Verifies that:
		- Hero inventory is extracted
		- Contains valid items (after filtering achievements, buffs, medals)
		- Items have valid kb_id and quantity fields

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None, "Hero inventory should be extracted"
		assert len(result.hero_inventory.items) > 100, f"Expected >100 items, got {len(result.hero_inventory.items)}"

		for item in result.hero_inventory.items:
			assert item.kb_id, "Each item should have kb_id"
			assert item.quantity > 0, f"Item {item.kb_id} should have positive quantity"

	def test_hero_inventory_first_items(self, parser, inventory_save_path):
		"""
		Test specific first items from hero inventory

		Verifies the first 5 items match expected values from research

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		items = result.hero_inventory.items
		items_dict = {item.kb_id: item.quantity for item in items}

		expected_items = {
			'addon3_magic_ingridients': 1,
			'kerus_sword': 1,
			'addon4_human_battle_mage_braces': 1,
			'flame_necklace': 1,
			'addon4_demon_pandemonic_gloves': 1
		}

		for kb_id, expected_quantity in expected_items.items():
			assert kb_id in items_dict, f"Item {kb_id} should be in hero inventory"
			assert items_dict[kb_id] == expected_quantity, \
				f"Item {kb_id}: expected quantity {expected_quantity}, got {items_dict[kb_id]}"

	def test_hero_inventory_stackable_items(self, parser, inventory_save_path):
		"""
		Test stackable items with high quantities

		Verifies that stackable items have correct quantities >1

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		items_dict = {item.kb_id: item.quantity for item in result.hero_inventory.items}

		stackable_items = {
			'addon4_spell_rock_holy_rain_100': 3,
			'addon4_spell_rock_resurrection_80': 6,
			'addon3_quest_hobo': 626,
			'addon3_quest_pow': 5767
		}

		for kb_id, expected_quantity in stackable_items.items():
			assert kb_id in items_dict, f"Stackable item {kb_id} should be in hero inventory"
			assert items_dict[kb_id] == expected_quantity, \
				f"Stackable item {kb_id}: expected quantity {expected_quantity}, got {items_dict[kb_id]}"

	def test_hero_inventory_no_achievements(self, parser, inventory_save_path):
		"""
		Test that achievements are filtered out

		Verifies that no items starting with 'achievement_' are in hero inventory

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		achievement_items = [
			item for item in result.hero_inventory.items
			if item.kb_id.startswith('achievement_')
		]

		assert len(achievement_items) == 0, \
			f"Hero inventory should not contain achievements, found: {[item.kb_id for item in achievement_items]}"

	def test_hero_inventory_no_metadata(self, parser, inventory_save_path):
		"""
		Test that metadata keywords are filtered out

		Verifies that no metadata keywords are in hero inventory

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		metadata_keywords = {'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd'}
		metadata_items = [
			item for item in result.hero_inventory.items
			if item.kb_id in metadata_keywords
		]

		assert len(metadata_items) == 0, \
			f"Hero inventory should not contain metadata, found: {[item.kb_id for item in metadata_items]}"

	def test_hero_inventory_no_buffs(self, parser, inventory_save_path):
		"""
		Test that buff entries (sp_*) are filtered out

		Verifies that no items starting with 'sp_' are in hero inventory

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		sp_items = [
			item for item in result.hero_inventory.items
			if item.kb_id.startswith('sp_')
		]

		assert len(sp_items) == 0, \
			f"Hero inventory should not contain buffs (sp_*), found: {[item.kb_id for item in sp_items]}"

	def test_hero_inventory_no_slbody(self, parser, inventory_save_path):
		"""
		Test that slbody entries are filtered out

		Verifies that no 'slbody' items are in hero inventory

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		slbody_items = [
			item for item in result.hero_inventory.items
			if item.kb_id == 'slbody'
		]

		assert len(slbody_items) == 0, \
			f"Hero inventory should not contain 'slbody', found {len(slbody_items)} occurrences"

	def test_hero_inventory_no_medals(self, parser, inventory_save_path):
		"""
		Test that medal entries are filtered out

		Verifies that no items starting with 'medal_' are in hero inventory

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		medal_items = [
			item for item in result.hero_inventory.items
			if item.kb_id.startswith('medal_')
		]

		assert len(medal_items) == 0, \
			f"Hero inventory should not contain medals (medal_*), found: {[item.kb_id for item in medal_items]}"

	def test_hero_inventory_no_stats_and_buffs(self, parser, inventory_save_path):
		"""
		Test that hero stats and talent buffs are filtered out

		Verifies that no hero stats (experience, defense, crystals) or
		talent buffs (hidden_*, warrior_bonus_*, demoness_*) are in inventory

		:param parser:
			SaveDataParser instance
		:param inventory_save_path:
			Path to test save file
		"""
		result = parser.parse(inventory_save_path)

		assert result.hero_inventory is not None

		bad_prefixes = ['hidden_', 'warrior_bonus_', 'demoness_']
		bad_stats = ['experience', 'defense', 'crystals']

		bad_items = [
			item for item in result.hero_inventory.items
			if any(item.kb_id.startswith(prefix) for prefix in bad_prefixes)
			or item.kb_id in bad_stats
		]

		assert len(bad_items) == 0, \
			f"Hero inventory should not contain stats/buffs, found: {[item.kb_id for item in bad_items]}"
