import typing
from abc import ABC, abstractmethod
from typing import Any

from src.domain.game.dto.ProfileSyncResult import ProfileSyncResult
from src.utils.parsers.save_data.SaveFileData import SaveFileData


class IProfileGameDataSyncerService(ABC):

	@abstractmethod
	def sync(
		self,
		data: SaveFileData,
		profile_id: int
	) -> ProfileSyncResult:
		"""
		Sync parsed shop inventory data to database

		:param data:
			Parsed shop data from parse() method
		:param profile_id:
			Profile ID to associate inventories with
		:return:
			ProfileSyncResult with counts and corrupted data
		"""
		pass