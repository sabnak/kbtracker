import pytest
import hashlib
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from src.domain.game.services.ProfileService import ProfileService
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.domain.game.dto.ProfileSyncResult import ProfileSyncResult, ProfileSyncShopResult, ProfileSyncHeroInventoryResult
from src.domain.exceptions import EntityNotFoundException, InvalidKbIdException


class TestProfileServiceScan:

	@pytest.fixture
	def mock_profile_repo(self):
		return Mock()

	@pytest.fixture
	def mock_save_file_service(self):
		return Mock()

	@pytest.fixture
	def mock_config(self):
		config = Mock()
		config.game_save_path = "/saves"
		return config

	@pytest.fixture
	def mock_data_syncer(self):
		return Mock()

	@pytest.fixture
	def mock_shop_inventory_repo(self):
		return Mock()

	@pytest.fixture
	def mock_hero_inventory_repo(self):
		return Mock()

	@pytest.fixture
	def service(
		self,
		mock_profile_repo,
		mock_save_file_service,
		mock_config,
		mock_data_syncer,
		mock_shop_inventory_repo,
		mock_hero_inventory_repo
	):
		return ProfileService(
			profile_repository=mock_profile_repo,
			save_file_service=mock_save_file_service,
			config=mock_config,
			data_syncer=mock_data_syncer,
			shop_inventory_repository=mock_shop_inventory_repo,
			hero_inventory_repository=mock_hero_inventory_repo
		)

	@pytest.fixture
	def sample_profile(self):
		return ProfileEntity(
			id=1,
			name="Test Hero",
			hash=hashlib.md5("Test Hero".encode('utf-8')).hexdigest(),
			full_name="Test Hero",
			save_dir="Darkside/1707047253",
			created_at=datetime.now()
		)

	def test_scan_success_with_all_types(
		self,
		service,
		mock_profile_repo,
		mock_save_file_service,
		mock_data_syncer,
		sample_profile,
		mock_config,
		tmp_path
	):
		"""Test successful scan with items, spells, units, garrison"""
		mock_profile_repo.get_by_id.return_value = sample_profile
		mock_config.game_save_path = str(tmp_path)

		save_dir = tmp_path / "Darkside" / "1707047253"
		save_dir.mkdir(parents=True)
		save_file = save_dir / "data"
		save_file.write_text("test save data")

		mock_save_file_service.find_profile_most_recent_save.return_value = save_file
		mock_save_file_service.scan_shop_inventory.return_value = {
			'm_zcom_1422': {
				'items': [{'name': 'sword', 'quantity': 1}],
				'spells': [{'name': 'fireball', 'quantity': 2}],
				'units': [{'name': 'archer', 'quantity': 10}],
				'garrison': [{'name': 'knight', 'quantity': 5}]
			}
		}

		mock_data_syncer.sync.return_value = ProfileSyncResult(
			shops=ProfileSyncShopResult(
				items=1,
				spells=1,
				units=1,
				garrison=1,
				missed_data=None
			),
			hero_inventory=ProfileSyncHeroInventoryResult(
				items=3,
				missed_data=None
			)
		)

		result = service.scan_most_recent_save(1)

		assert isinstance(result, ProfileSyncResult)
		assert result.shops.items == 1
		assert result.shops.spells == 1
		assert result.shops.units == 1
		assert result.shops.garrison == 1
		assert result.shops.missed_data is None
		assert result.hero_inventory.items == 3
		mock_data_syncer.sync.assert_called_once()
		mock_profile_repo.update.assert_called_once()

	def test_scan_profile_not_found(self, service, mock_profile_repo):
		"""Test scan when profile doesn't exist"""
		mock_profile_repo.get_by_id.return_value = None

		with pytest.raises(EntityNotFoundException) as exc:
			service.scan_most_recent_save(999)

		assert "Profile" in str(exc.value)
		assert "999" in str(exc.value)

	def test_scan_no_matching_save_file(
		self,
		service,
		mock_profile_repo,
		mock_save_file_service,
		sample_profile,
		mock_config,
		tmp_path
	):
		"""Test scan when no save file matches profile hash"""
		mock_profile_repo.get_by_id.return_value = sample_profile
		mock_config.game_save_path = str(tmp_path)

		save_dir = tmp_path / "Darkside" / "1707047253"
		save_dir.mkdir(parents=True)
		save_file = save_dir / "data"
		save_file.write_text("test save data")

		mock_save_file_service.find_profile_most_recent_save.side_effect = FileNotFoundError("No matching save found")

		with pytest.raises(FileNotFoundError):
			service.scan_most_recent_save(1)

	def test_scan_invalid_kb_id_propagates(
		self,
		service,
		mock_profile_repo,
		mock_save_file_service,
		mock_data_syncer,
		sample_profile,
		mock_config,
		tmp_path
	):
		"""Test that InvalidKbIdException propagates from parser"""
		mock_profile_repo.get_by_id.return_value = sample_profile
		mock_config.game_save_path = str(tmp_path)

		save_dir = tmp_path / "Darkside" / "1707047253"
		save_dir.mkdir(parents=True)
		save_file = save_dir / "data"
		save_file.write_text("test save data")

		mock_save_file_service.find_profile_most_recent_save.return_value = save_file
		mock_save_file_service.scan_shop_inventory.return_value = {}
		mock_data_syncer.sync.side_effect = InvalidKbIdException('invalid_item', 'shop_1422')

		with pytest.raises(InvalidKbIdException) as exc:
			service.scan_most_recent_save(1)

		assert 'invalid_item' in str(exc.value)

	def test_scan_empty_inventories(
		self,
		service,
		mock_profile_repo,
		mock_save_file_service,
		mock_data_syncer,
		sample_profile,
		mock_config,
		tmp_path
	):
		"""Test scan with empty shop inventories"""
		mock_profile_repo.get_by_id.return_value = sample_profile
		mock_config.game_save_path = str(tmp_path)

		save_dir = tmp_path / "Darkside" / "1707047253"
		save_dir.mkdir(parents=True)
		save_file = save_dir / "data"
		save_file.write_text("test save data")

		mock_save_file_service.find_profile_most_recent_save.return_value = save_file
		mock_save_file_service.scan_shop_inventory.return_value = {
			'm_zcom_1422': {
				'items': [],
				'spells': [],
				'units': [],
				'garrison': []
			}
		}

		mock_data_syncer.sync.return_value = ProfileSyncResult(
			shops=ProfileSyncShopResult(
				items=0,
				spells=0,
				units=0,
				garrison=0,
				missed_data=None
			),
			hero_inventory=ProfileSyncHeroInventoryResult(
				items=0,
				missed_data=None
			)
		)

		result = service.scan_most_recent_save(1)

		assert isinstance(result, ProfileSyncResult)
		assert result.shops.items == 0
		assert result.shops.spells == 0
		assert result.shops.units == 0
		assert result.shops.garrison == 0
		assert result.shops.missed_data is None
		assert result.hero_inventory.items == 0

	def test_scan_multiple_saves_selects_most_recent(
		self,
		service,
		mock_profile_repo,
		mock_save_file_service,
		mock_data_syncer,
		sample_profile,
		mock_config,
		tmp_path
	):
		"""Test that scan selects the most recent save file"""
		import time

		mock_profile_repo.get_by_id.return_value = sample_profile
		mock_config.game_save_path = str(tmp_path)

		darkside_dir = tmp_path / "Darkside"
		darkside_dir.mkdir()

		save1 = darkside_dir / "quick1707047253" / "data"
		save1.parent.mkdir()
		save1.write_text("old save")

		time.sleep(0.01)

		save2 = darkside_dir / "1707047999" / "data"
		save2.parent.mkdir()
		save2.write_text("new save")

		mock_save_file_service.find_profile_most_recent_save.return_value = save2
		mock_save_file_service.scan_save_data.return_value = Mock()

		mock_data_syncer.sync.return_value = ProfileSyncResult(
			shops=ProfileSyncShopResult(
				items=0,
				spells=0,
				units=0,
				garrison=0,
				missed_data=None
			),
			hero_inventory=ProfileSyncHeroInventoryResult(
				items=0,
				missed_data=None
			)
		)

		result = service.scan_most_recent_save(1)

		mock_save_file_service.find_profile_most_recent_save.assert_called_once_with(sample_profile)
		mock_save_file_service.scan_save_data.assert_called_once_with(save2)
