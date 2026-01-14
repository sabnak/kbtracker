"""
Extract info files from all test save files
"""
from pathlib import Path
import zipfile
import tempfile

SAVES = [
    ("/app/tests/game_files/saves_archive/orcs_endgame.sav", "orcs_endgame"),
    ("/app/tests/game_files/saves_archive/orcs_startgame.sav", "orcs_startgame"),
    ("/app/tests/game_files/saves_archive/red_sands_Quicksave1.sav", "red_sands"),
    ("/app/tests/game_files/saves/quick1768258578", "quick1768258578"),
    ("/app/tests/game_files/saves/1707047253", "save_1707047253"),
]

OUTPUT_DIR = Path(__file__).parent / "tmp"
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_info_file(save_path: Path, output_name: str) -> None:
	"""
	Extract info file from save (archive or directory)

	:param save_path:
		Path to save file
	:param output_name:
		Output file name prefix
	"""
	if not save_path.exists():
		print(f"SKIP: {save_path} not found")
		return

	# Handle .sav archives and directories differently
	if save_path.suffix == ".sav":
		with tempfile.TemporaryDirectory() as temp_dir:
			with zipfile.ZipFile(save_path, "r") as zf:
				zf.extractall(temp_dir)

			# Try both info and saveinfo
			info_path = Path(temp_dir) / "info"
			if not info_path.exists():
				info_path = Path(temp_dir) / "saveinfo"

			if info_path.exists():
				info_data = info_path.read_bytes()
				output_file = OUTPUT_DIR / f"{output_name}_info.bin"
				output_file.write_bytes(info_data)
				print(f"OK: {output_name} → {len(info_data)} bytes")
			else:
				print(f"FAIL: No info file in {output_name}")
	else:
		# Directory save
		info_path = save_path / "info"
		if not info_path.exists():
			info_path = save_path / "saveinfo"

		if info_path.exists():
			info_data = info_path.read_bytes()
			output_file = OUTPUT_DIR / f"{output_name}_info.bin"
			output_file.write_bytes(info_data)
			print(f"OK: {output_name} → {len(info_data)} bytes")
		else:
			print(f"FAIL: No info file in {output_name}")


if __name__ == "__main__":
	print("Extracting info files from test saves...")
	print()

	for save_path_str, name in SAVES:
		extract_info_file(Path(save_path_str), name)

	print()
	print("Extraction complete!")
	print(f"Files saved to: {OUTPUT_DIR}")
