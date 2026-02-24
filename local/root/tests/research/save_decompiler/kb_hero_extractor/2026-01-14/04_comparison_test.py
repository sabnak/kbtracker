"""
Compare info file parser vs current data file parser
"""
from pathlib import Path
import sys

sys.path.insert(0, "/app")

from src.utils.parsers.save_data.HeroSaveParser import HeroSaveParser
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.utils.parsers.save_data.DataFileType import DataFileType

# Import our new info parser
exec(open("/app/tests/research/save_decompiler/kb_hero_extractor/2026-01-14/03_info_parser_v1.py").read())


def test_save(save_path: Path, expected_first: str, expected_second: str) -> None:
	"""
	Compare both parsers on a save file

	:param save_path:
		Path to save file
	:param expected_first:
		Expected first name
	:param expected_second:
		Expected second name
	"""
	print(f"\n{'='*70}")
	print(f"Testing: {save_path.name}")
	print(f"{'='*70}")

	# Current data file parser
	data_parser = HeroSaveParser()
	data_result = data_parser.parse(save_path)

	# New info file parser
	decompressor = SaveFileDecompressor()
	info_data = decompressor.decompress(save_path, DataFileType.INFO)
	info_result = parse_hero_name_from_info(info_data)

	# Compare
	print(f"\nExpected:")
	print(f"  first_name:  '{expected_first}'")
	print(f"  second_name: '{expected_second}'")

	print(f"\nCurrent (data file) parser:")
	print(f"  first_name:  '{data_result['first_name']}'")
	print(f"  second_name: '{data_result['second_name']}'")
	data_correct = (
		data_result['first_name'] == expected_first and
		data_result['second_name'] == expected_second
	)
	print(f"  Status: {'✓ CORRECT' if data_correct else '✗ WRONG'}")

	print(f"\nNew (info file) parser:")
	print(f"  first_name:  '{info_result['first_name']}'")
	print(f"  second_name: '{info_result['second_name']}'")
	info_correct = (
		info_result['first_name'] == expected_first and
		info_result['second_name'] == expected_second
	)
	print(f"  Status: {'✓ CORRECT' if info_correct else '✗ WRONG'}")

	return data_correct, info_correct


if __name__ == "__main__":
	print("Comparing data file parser vs info file parser...")

	test_cases = [
		(Path("/app/tests/game_files/saves_archive/orcs_endgame.sav"), "Зачарованная", ""),
		(Path("/app/tests/game_files/saves_archive/orcs_startgame.sav"), "Справедливая", ""),
		(Path("/app/tests/game_files/saves_archive/red_sands_Quicksave1.sav"), "Отважная", ""),
		(Path("/app/tests/game_files/saves/quick1768258578"), "Даэрт", "де Мортон"),
		(Path("/app/tests/game_files/saves/1707047253"), "Неолина", "Очаровательная"),
	]

	data_correct_count = 0
	info_correct_count = 0

	for save_path, expected_first, expected_second in test_cases:
		data_correct, info_correct = test_save(save_path, expected_first, expected_second)
		if data_correct:
			data_correct_count += 1
		if info_correct:
			info_correct_count += 1

	print(f"\n{'='*70}")
	print(f"SUMMARY")
	print(f"{'='*70}")
	print(f"Data file parser: {data_correct_count}/{len(test_cases)} correct")
	print(f"Info file parser: {info_correct_count}/{len(test_cases)} correct")

	if info_correct_count > data_correct_count:
		print(f"\n✓ Info file parser is more reliable!")
	elif info_correct_count == data_correct_count == len(test_cases):
		print(f"\n✓ Both parsers work perfectly!")
	else:
		print(f"\n⚠ Results vary")
