import pytest
from pathlib import Path
from typing import Any


@pytest.mark.smoke
class TestShopInventoryParser:

	"""
	Smoke tests for ShopInventoryParser using real save files

	CRITICAL: Manual execution only - excluded from CI/CD
	Run with: pytest -m smoke tests/smoke/
	"""

	@staticmethod
	def _assert_inventory_section_match(
		actual: list[dict[str, Any]],
		expected: list[dict[str, Any]],
		section_name: str
	) -> None:
		"""
		Assert deep equality of inventory section

		Compares actual parsed data against expected reference data.
		Provides specific error messages for debugging failures.

		:param actual:
			Parsed inventory section from parser
		:param expected:
			Expected inventory section (reference data)
		:param section_name:
			Section identifier for error messages (garrison, items, units, spells)
		"""
		assert len(actual) == len(expected), \
			f"{section_name}: Expected {len(expected)} items, got {len(actual)}"

		actual_sorted = sorted(actual, key=lambda x: x['name'])
		expected_sorted = sorted(expected, key=lambda x: x['name'])

		for i, (act_item, exp_item) in enumerate(zip(actual_sorted, expected_sorted)):
			assert act_item['name'] == exp_item['name'], \
				f"{section_name}[{i}]: Name mismatch - expected '{exp_item['name']}', got '{act_item['name']}'"
			assert act_item['quantity'] == exp_item['quantity'], \
				f"{section_name}[{i}] ({act_item['name']}): Quantity mismatch - expected {exp_item['quantity']}, got {act_item['quantity']}"

	def test_shop_itext_m_zcom_1422_inventory(
		self,
		shop_inventory_parser,
		test_save_1707047253_path: Path
	) -> None:
		"""
		Smoke test: Verify complete inventory for shop itext_m_zcom_1422

		Uses real save file 1707047253 to validate:
		- Garrison parsing (3 units)
		- Items parsing (11 items)
		- Units parsing (39 units)
		- Spells parsing (30 spells)

		:param shop_inventory_parser:
			ShopInventoryParser instance
		:param test_save_1707047253_path:
			Path to save data file
		"""
		result = shop_inventory_parser.parse(test_save_1707047253_path)

		shop_id = "m_zcom_1422"
		inventory = None
		for shop_data in result:
			if shop_data.get('itext') == shop_id:
				inventory = shop_data['inventory']
				break
		assert inventory, f"Shop {shop_id} not found in parsed results"

		expected_garrison = [
			{"name": "dread_eye", "quantity": 53},
			{"name": "cyclop", "quantity": 27},
			{"name": "gargoyle", "quantity": 159}
		]

		expected_items = [
			{"name": "addon4_dwarf_shield_generator", "quantity": 1},
			{"name": "addon4_dwarf_simple_belt", "quantity": 1},
			{"name": "addon4_elf_bird_armor", "quantity": 1},
			{"name": "addon4_elf_botanic_book", "quantity": 1},
			{"name": "addon4_elf_fairy_amulet", "quantity": 1},
			{"name": "addon4_human_life_cup", "quantity": 1},
			{"name": "dragon_heart", "quantity": 1},
			{"name": "exorcist_necklace", "quantity": 1},
			{"name": "fire_master_braces", "quantity": 1},
			{"name": "moon_sword", "quantity": 1},
			{"name": "tournament_helm", "quantity": 1}
		]

		expected_units = [
			{"name": "dark_ethereal", "quantity": 8273},
			{"name": "dark_priest", "quantity": 1220},
			{"name": "dark_bowman", "quantity": 696},
			{"name": "icemage", "quantity": 3204},
			{"name": "dark_horseman", "quantity": 50},
			{"name": "dark_sprite", "quantity": 8800},
			{"name": "dark_dryad", "quantity": 1375},
			{"name": "dark_elf", "quantity": 2849},
			{"name": "dark_druid", "quantity": 2896},
			{"name": "dark_ent", "quantity": 552},
			{"name": "dark_blacksmith", "quantity": 35875},
			{"name": "dark_miner", "quantity": 17641},
			{"name": "dark_dwarf", "quantity": 1394},
			{"name": "dark_ingeneer", "quantity": 2629},
			{"name": "dark_alchemist", "quantity": 857},
			{"name": "dark_peasant", "quantity": 28000},
			{"name": "dark_footman2", "quantity": 300},
			{"name": "dark_archmage", "quantity": 1150},
			{"name": "dark_sprite_lake", "quantity": 28000},
			{"name": "dark_satyr", "quantity": 16500},
			{"name": "dark_werewolf", "quantity": 1300},
			{"name": "dark_elf2", "quantity": 100},
			{"name": "dark_cannoner", "quantity": 422},
			{"name": "dark_priest2", "quantity": 2500},
			{"name": "dark_powerman", "quantity": 250},
			{"name": "dark_runemage", "quantity": 140},
			{"name": "dark_unicorn", "quantity": 800},
			{"name": "dark_hawk", "quantity": 110},
			{"name": "dark_runemaster", "quantity": 1000},
			{"name": "dark_underguard", "quantity": 750},
			{"name": "dark_giant", "quantity": 140},
			{"name": "dark_priestes", "quantity": 6000},
			{"name": "dark_clown", "quantity": 1000},
			{"name": "dark_knight", "quantity": 300},
			{"name": "dark_unicorn_runic", "quantity": 300},
			{"name": "dark_ent2", "quantity": 30},
			{"name": "dark_footman", "quantity": 10000},
			{"name": "dark_paladin", "quantity": 500},
			{"name": "dark_elf3", "quantity": 500},
			{"name": "dark_dwarf_trapper", "quantity": 2000}
		]

		expected_spells = [
			{"name": "spell_blind", "quantity": 1},
			{"name": "spell_chaos_coagulate", "quantity": 2},
			{"name": "spell_cold_grasp", "quantity": 2},
			{"name": "spell_defenseless", "quantity": 1},
			{"name": "spell_demonologist", "quantity": 1},
			{"name": "spell_desintegration", "quantity": 4},
			{"name": "spell_dispell", "quantity": 4},
			{"name": "spell_dragon_arrow", "quantity": 2},
			{"name": "spell_empathy", "quantity": 4},
			{"name": "spell_fire_breath", "quantity": 3},
			{"name": "spell_fire_shield", "quantity": 1},
			{"name": "spell_ghost_sword", "quantity": 2},
			{"name": "spell_gold_rush", "quantity": 4},
			{"name": "spell_healing", "quantity": 6},
			{"name": "spell_holy_rain", "quantity": 1},
			{"name": "spell_horde_totem", "quantity": 1},
			{"name": "spell_kamikaze", "quantity": 2},
			{"name": "spell_life_stealer", "quantity": 2},
			{"name": "spell_lull", "quantity": 7},
			{"name": "spell_magic_source", "quantity": 2},
			{"name": "spell_mine_field", "quantity": 2},
			{"name": "spell_pain_mirror", "quantity": 2},
			{"name": "spell_plague", "quantity": 1},
			{"name": "spell_raise_dead", "quantity": 3},
			{"name": "spell_revival", "quantity": 2},
			{"name": "spell_scare", "quantity": 3},
			{"name": "spell_shifted_time", "quantity": 2},
			{"name": "spell_slow", "quantity": 1},
			{"name": "spell_undertaker", "quantity": 3},
			{"name": "spell_wasp_swarm", "quantity": 1},
			{"name": "spell_weakness", "quantity": 1},
			{"name": "spell_winter_dance", "quantity": 1}
		]

		self._assert_inventory_section_match(inventory["garrison"], expected_garrison, "garrison")
		self._assert_inventory_section_match(inventory["items"], expected_items, "items")
		self._assert_inventory_section_match(inventory["units"], expected_units, "units")
		self._assert_inventory_section_match(inventory["spells"], expected_spells, "spells")
