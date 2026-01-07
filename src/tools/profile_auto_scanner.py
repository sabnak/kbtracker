import argparse
from pathlib import Path

import pydantic

from src.tools.CLITool import CLITool, T
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.domain.game.dto.ProfileSyncResult import ProfileSyncResult
from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.domain.app.interfaces.IGameService import IGameService
from src.domain.game.interfaces.ISchemaManagementService import ISchemaManagementService
from src.domain.base.repositories.CrudRepository import GAME_CONTEXT
from src.web.dependencies.game_context import GameContext


class LaunchParams(pydantic.BaseModel):

	pass


class ProfileAutoScannerCLI(CLITool[LaunchParams]):

	def _build_params(self) -> T:
		"""
		Build launch parameters from command-line arguments

		:return:
			LaunchParams instance
		"""
		p = argparse.ArgumentParser(description='Profile Auto-Scanner')
		p.parse_args()
		return LaunchParams()

	def _run(self) -> None:
		"""
		Main tool execution logic

		:return:
		"""
		game_service = self._container.game_service()
		schema_mgmt = self._container.schema_management_service()
		profile_service = self._container.profile_service()
		save_file_service = self._container.save_file_service()

		all_games = game_service.list_games()

		if not all_games:
			print("No games found.")
			return

		for game in all_games:
			schema_name = schema_mgmt.get_schema_name(game.id)
			game_context = GameContext(game.id, schema_name)
			GAME_CONTEXT.set(game_context)

			print(f"\n=== Processing Game: {game.name} (ID: {game.id}, Schema: {schema_name}) ===")

			all_profiles = profile_service.list_profiles()
			auto_scan_profiles = [p for p in all_profiles if p.is_auto_scan_enabled]

			if not auto_scan_profiles:
				print(f"No profiles with auto-scan enabled found for game '{game.name}'.")
				continue

			for profile in auto_scan_profiles:
				self._process_profile(profile, profile_service, save_file_service)

	def _process_profile(
		self,
		profile: ProfileEntity,
		profile_service: IProfileService,
		save_file_service: ISaveFileService
	) -> None:
		"""
		Process a single profile: check for new saves and scan if needed

		:param profile:
			Profile to process
		:param profile_service:
			Profile service instance
		:param save_file_service:
			Save file service instance
		:return:
		"""
		try:
			save_path = save_file_service.find_profile_most_recent_save(profile)
		except FileNotFoundError:
			print(f"Profile {profile.name}<{profile.id}> save error: no save file found")
			return

		save_mtime = int(save_path.stat().st_mtime)
		last_timestamp = profile.last_save_timestamp or 0

		if save_mtime > last_timestamp:
			result = profile_service.scan_save(profile, save_path)
			self._print_scan_result(profile, "scanned", result)
		else:
			print(f"Profile {profile.name}<{profile.id}> save skipped (outdated). Result: No scan performed")

	def _print_scan_result(
		self,
		profile: ProfileEntity,
		status: str,
		result: ProfileSyncResult
	) -> None:
		"""
		Print scan result for a profile

		:param profile:
			Profile that was scanned
		:param status:
			Scan status (scanned, skipped, etc.)
		:param result:
			ProfileSyncResult with counts
		:return:
		"""
		result_str = f"items={result.items}, spells={result.spells}, units={result.units}, garrison={result.garrison}"
		print(f"Profile {profile.name}<{profile.id}> save {status}. Result: {result_str}")


if __name__ == '__main__':
	ProfileAutoScannerCLI().run()
