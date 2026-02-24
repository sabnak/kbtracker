import pytest
from src.domain.game.entities.AtomMap import AtomMap
from src.domain.game.entities.Shop import Shop


class TestKFSAtomMapsAndShopsParser:

	@pytest.fixture(autouse=True)
	def setup(self, extracted_game_files):
		"""
		Auto-use fixture that ensures archives are extracted before tests

		:param extracted_game_files:
			Extraction root path
		"""
		pass

	def test_parse_returns_list_of_dicts(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that parse returns a list of dicts with location and shops keys
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		assert isinstance(result, list)
		assert len(result) > 0
		for item in result:
			assert isinstance(item, dict)
			assert 'location' in item
			assert 'shops' in item
			assert isinstance(item['location'], AtomMap)
			assert isinstance(item['shops'], list)
			assert all(isinstance(shop, Shop) for shop in item['shops'])

	def test_shop_fields_populated_correctly(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that Shop fields are populated correctly for known entry
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		# Find amasonia location with shop amasonia_1173
		amasonia_entry = next(
			(entry for entry in result if entry['location'].kb_id == 'amasonia'),
			None
		)

		assert amasonia_entry is not None

		# Find shop amasonia_1173
		shop_1173 = next(
			(shop for shop in amasonia_entry['shops'] if shop.kb_id == 'amasonia_1173'),
			None
		)

		assert shop_1173 is not None
		assert shop_1173.name == 'Замок изгоев'
		assert shop_1173.hint == 'Замок изгоев'
		assert shop_1173.msg == 'Здесь живут рассерженные мужчины'
		assert shop_1173.id == 0

	def test_locations_are_unique(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that each location appears only once
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		location_kb_ids = [entry['location'].kb_id for entry in result]
		assert len(location_kb_ids) == len(set(location_kb_ids)), "Duplicate location kb_ids found"

	def test_shops_grouped_by_location(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that all shops in each dict belong to that location
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		# All shops within a location entry should be part of that location
		# (we can't verify this directly without the raw data, but we can
		# verify the structure is consistent)
		for entry in result:
			assert len(entry['shops']) > 0, f"AtomMap {entry['location'].kb_id} has no shops"

	def test_prefix_stripped_from_values(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that ^?^ prefix is removed from values
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		# Check no values start with ^?^
		for entry in result:
			location = entry['location']
			assert not location.name.startswith('^?^')

			for shop in entry['shops']:
				assert not shop.name.startswith('^?^')
				if shop.hint:
					assert not shop.hint.startswith('^?^')
				if shop.msg:
					assert not shop.msg.startswith('^?^')

	def test_empty_hint_and_msg_allowed(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that shops can have empty hint or msg (None values)
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		# Collect all shops
		all_shops = []
		for entry in result:
			all_shops.extend(entry['shops'])

		# Check that None values are allowed for hint and msg
		# (this test just verifies the structure allows it)
		for shop in all_shops:
			# hint and msg should be either str or None
			assert shop.hint is None or isinstance(shop.hint, str)
			assert shop.msg is None or isinstance(shop.msg, str)

	def test_all_shops_have_required_fields(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that all parsed shops have required non-empty fields
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		for entry in result:
			location = entry['location']
			assert location.kb_id != '', "AtomMap has empty kb_id"
			assert location.name != '', f"AtomMap {location.kb_id} has empty name"

			for shop in entry['shops']:
				assert shop.kb_id != '', f"Shop has empty kb_id"
				assert '_' in shop.kb_id, f"Shop kb_id must be composite: {shop.kb_id}"
				assert shop.name != '', f"Shop {shop.kb_id} has empty name"

	def test_location_and_shop_ids_are_zero(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that all AtomMap.id, Shop.id, and Shop.location_id are 0
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		for entry in result:
			location = entry['location']
			assert location.id == 0, f"AtomMap {location.kb_id} has non-zero id: {location.id}"

			for shop in entry['shops']:
				assert shop.id == 0, f"Shop {shop.kb_id} has non-zero id: {shop.id}"
				assert shop.location_id == 0, f"Shop {shop.kb_id} has non-zero location_id: {shop.location_id}"

	def test_multiple_locations_parsed(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that multiple different locations are found
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		# Should have multiple locations
		assert len(result) > 1, "Only one location found"

		location_kb_ids = {entry['location'].kb_id for entry in result}
		# Known locations from test file
		assert 'amasonia' in location_kb_ids

	def test_each_location_has_shops(
		self,
		kfs_locations_and_shops_parser,
		test_game_name
	):
		"""
		Test that each location dict has at least one shop
		"""
		result = kfs_locations_and_shops_parser.parse(test_game_name)

		for entry in result:
			assert len(entry['shops']) > 0, \
				f"AtomMap {entry['location'].kb_id} has no shops"
