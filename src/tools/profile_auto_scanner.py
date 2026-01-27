import argparse

import pydantic

from src.domain.app.entities.Game import Game
from src.tools.CLITool import CLITool, T
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
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
		self._log("Starting...")
		game_service = self._container.game_service()
		schema_mgmt = self._container.schema_management_service()
		profile_service = self._container.profile_service()
		save_file_service = self._container.save_file_service()

		all_games = game_service.list_games()

		if not all_games:
			self._log("No games found.")
			return

		for game in all_games:
			schema_name = schema_mgmt.get_schema_name(game.id)
			game_context = GameContext(game.id, schema_name)
			GAME_CONTEXT.set(game_context)

			all_profiles = profile_service.list_profiles()
			auto_scan_profiles = [p for p in all_profiles if p.is_auto_scan_enabled]

			if not auto_scan_profiles:
				self._log(f"No profiles with auto-scan enabled found.", game=game)
				continue
			self._log(f"{len(auto_scan_profiles)} profiles with auto-scan enabled found.", game=game)

			for profile in auto_scan_profiles:
				self._process_profile(profile, game, profile_service, save_file_service)

	def _process_profile(
		self,
		profile: ProfileEntity,
		game: Game,
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
			self._log(f"Profile save error: no save file found", game=game, profile=profile)
			return

		save_mtime = int(save_path.stat().st_mtime)
		last_timestamp = profile.last_save_timestamp or 0

		if save_mtime <= last_timestamp:
			self._log(f"Profile save skipped (outdated). Result: No scan performed", game=game, profile=profile)
			return

		result = profile_service.scan_save(profile, save_path)
		result_str = (f"items={result.shops.items}, spells={result.shops.spells}, "
		              f"units={result.shops.units}, garrison={result.shops.garrison}; inventory={result.hero_inventory.items}")
		self._log(f"Profile saved scanned. Result: {result_str}", game=game, profile=profile)

	def _log(self, msg: str, game: Game = None, profile: ProfileEntity = None):
		self._logger.info(
			f"[Scanner] {f'Game: {game.name}' if game else ''} "
			f"{f'Profile: {profile.name}<{profile.id}>' if profile else ''} "
			f"- {msg}"
		)


if __name__ == '__main__':
	ProfileAutoScannerCLI().run()
