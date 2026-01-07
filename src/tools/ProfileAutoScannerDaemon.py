import time
import sched
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

import pydantic

from src.tools.CLITool import CLITool, T
from src.domain.app.interfaces.ISettingsService import ISettingsService


class LaunchParams(pydantic.BaseModel):

	pass


class ProfileAutoScannerDaemon(CLITool[LaunchParams]):

	DAEMON_LIFETIME_HOURS: int = 24
	SETTINGS_CHECK_INTERVAL_SECONDS: int = 60
	SCANNER_TIMEOUT_SECONDS: int = 600

	_scheduler: sched.scheduler
	_settings_service: ISettingsService
	_start_time: datetime
	_current_scan_frequency: int
	_scanner_script_path: Path

	def _build_params(self) -> LaunchParams:
		"""
		Build launch parameters from command-line arguments

		:return:
			Empty LaunchParams instance
		"""
		return LaunchParams()

	def _run(self) -> None:
		"""
		Main daemon execution loop

		Initializes daemon, schedules jobs, and runs scheduler until lifetime expires.

		:return:
		"""
		self._log("Profile Auto-Scanner Daemon started")
		self._log(f"Lifetime: {self.DAEMON_LIFETIME_HOURS} hours")

		self._initialize_daemon()

		self._schedule_settings_check()
		self._schedule_scanner_job()

		try:
			self._scheduler.run()
		except KeyboardInterrupt:
			self._log("Daemon interrupted by user")

		self._log("Daemon shutdown complete")

	def _initialize_daemon(self) -> None:
		"""
		Initialize daemon state and dependencies

		Sets up scheduler, fetches initial settings, resolves scanner path.

		:return:
		"""
		self._scheduler = sched.scheduler(time.time, time.sleep)
		self._settings_service = self._container.settings_service()
		self._start_time = datetime.now()

		settings = self._settings_service.get_settings()
		self._current_scan_frequency = settings.scan_frequency

		self._scanner_script_path = Path(__file__).parent / "profile_auto_scanner.py"

		self._log(f"Daemon initialized. Scan frequency: {self._current_scan_frequency} minutes")

	def _schedule_settings_check(self) -> None:
		"""
		Schedule next settings check job

		Checks lifetime before scheduling. Settings checks run every 60 seconds.

		:return:
		"""
		if self._is_lifetime_expired():
			self._log("Lifetime expired, not scheduling settings check")
			return

		self._scheduler.enter(
			self.SETTINGS_CHECK_INTERVAL_SECONDS,
			priority=1,
			action=self._check_settings
		)

	def _schedule_scanner_job(self) -> None:
		"""
		Schedule next scanner execution

		Checks lifetime before scheduling. Uses current scan_frequency for delay.

		:return:
		"""
		if self._is_lifetime_expired():
			self._log("Lifetime expired, not scheduling scanner")
			return

		delay_seconds = self._current_scan_frequency * 60
		self._scheduler.enter(
			delay_seconds,
			priority=2,
			action=self._run_scanner
		)

		self._log(f"Scanner scheduled in {self._current_scan_frequency} minutes")

	def _check_settings(self) -> None:
		"""
		Check for settings changes and detect scan_frequency updates

		Updates internal state if frequency changed. Always reschedules next check.

		:return:
		"""
		try:
			settings = self._settings_service.get_settings()
			new_frequency = settings.scan_frequency

			if new_frequency != self._current_scan_frequency:
				self._log(
					f"Scan frequency changed: {self._current_scan_frequency} -> {new_frequency} minutes"
				)
				self._current_scan_frequency = new_frequency

		except Exception as e:
			self._log_error(f"Failed to check settings: {e}")

		self._schedule_settings_check()

	def _run_scanner(self) -> None:
		"""
		Execute profile_auto_scanner as subprocess

		Runs scanner with timeout, logs output, handles errors. Always reschedules next scan.

		:return:
		"""
		self._log("Starting profile auto-scanner...")

		try:
			result = subprocess.run(
				[sys.executable, str(self._scanner_script_path)],
				capture_output=True,
				text=True,
				timeout=self.SCANNER_TIMEOUT_SECONDS
			)

			if result.returncode == 0:
				self._log("Scanner completed successfully")
				if result.stdout:
					print(result.stdout)
			else:
				self._log_error(f"Scanner failed with exit code {result.returncode}")
				if result.stderr:
					print(result.stderr, file=sys.stderr)

		except subprocess.TimeoutExpired:
			self._log_error(f"Scanner timed out after {self.SCANNER_TIMEOUT_SECONDS} seconds")
		except Exception as e:
			self._log_error(f"Scanner execution failed: {e}")

		self._schedule_scanner_job()

	def _is_lifetime_expired(self) -> bool:
		"""
		Check if 24-hour lifetime has expired

		:return:
			True if daemon has been running for 24+ hours
		"""
		elapsed = datetime.now() - self._start_time
		return elapsed >= timedelta(hours=self.DAEMON_LIFETIME_HOURS)

	def _log(self, message: str) -> None:
		"""
		Log informational message with timestamp

		:param message:
			Message to log
		:return:
		"""
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print(f"[{timestamp}] [DAEMON] {message}")

	def _log_error(self, message: str) -> None:
		"""
		Log error message with timestamp to stderr

		:param message:
			Error message to log
		:return:
		"""
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print(f"[{timestamp}] [DAEMON] ERROR: {message}", file=sys.stderr)


if __name__ == '__main__':
	ProfileAutoScannerDaemon().run()
