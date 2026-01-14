"""
Info file parser v1 - Extract hero name from info file

Format discovered:
- Info file has key-value structure
- Pattern: [key_name_length (uint32)] [key_name (ASCII)] [value_length (uint32)] [value_data]
- Hero name field: "name" → UTF-16LE encoded string
- For two-name heroes, there's also "nickname" field with second name
"""
from pathlib import Path
import struct


def parse_hero_name_from_info(info_data: bytes) -> dict[str, str]:
	"""
	Extract hero name from info file data

	:param info_data:
		Raw info file bytes
	:return:
		Dictionary with first_name and second_name
	"""
	# Find "name" field
	name_marker = b"name"
	name_pos = info_data.find(name_marker)

	if name_pos == -1:
		return {"first_name": "", "second_name": ""}

	# Read length after "name" (uint32)
	if name_pos + 4 + 4 > len(info_data):
		return {"first_name": "", "second_name": ""}

	name_length = struct.unpack("<I", info_data[name_pos+4:name_pos+8])[0]

	# Validate length (this is character count, not byte count)
	if name_length <= 0 or name_length > 100:
		return {"first_name": "", "second_name": ""}

	# Read hero name (UTF-16LE: 2 bytes per character)
	name_start = name_pos + 8
	name_byte_length = name_length * 2  # UTF-16LE uses 2 bytes per character
	name_end = name_start + name_byte_length

	if name_end > len(info_data):
		return {"first_name": "", "second_name": ""}

	try:
		first_name = info_data[name_start:name_end].decode("utf-16-le")
	except:
		return {"first_name": "", "second_name": ""}

	# Look for "nickname" field (second name)
	nickname_marker = b"nickname"
	nickname_pos = info_data.find(nickname_marker, name_end)

	second_name = ""
	if nickname_pos != -1:
		# Read length after "nickname" (uint32)
		if nickname_pos + 8 + 4 <= len(info_data):
			nickname_length = struct.unpack("<I", info_data[nickname_pos+8:nickname_pos+12])[0]

			if 0 < nickname_length <= 100:
				nickname_start = nickname_pos + 12
				nickname_byte_length = nickname_length * 2  # UTF-16LE uses 2 bytes per character
				nickname_end = nickname_start + nickname_byte_length

				if nickname_end <= len(info_data):
					try:
						second_name = info_data[nickname_start:nickname_end].decode("utf-16-le")
					except:
						pass

	return {
		"first_name": first_name,
		"second_name": second_name
	}


if __name__ == "__main__":
	print("Testing info file parser...")
	print()

	samples_dir = Path(__file__).parent / "extracted_samples"

	test_cases = [
		("orcs_endgame_info.bin", "Зачарованная", ""),
		("orcs_startgame_info.bin", "Справедливая", ""),
		("red_sands_info.bin", "Отважная", ""),
		("quick1768258578_info.bin", "Даэрт", "де Мортон"),
		("save_1707047253_info.bin", "Неолина", "Очаровательная"),
	]

	all_passed = True

	for filename, expected_first, expected_second in test_cases:
		info_path = samples_dir / filename
		info_data = info_path.read_bytes()

		result = parse_hero_name_from_info(info_data)

		passed = (
			result["first_name"] == expected_first and
			result["second_name"] == expected_second
		)

		status = "✓ PASS" if passed else "✗ FAIL"
		print(f"{status} {filename}")
		print(f"  Expected: first='{expected_first}', second='{expected_second}'")
		print(f"  Got:      first='{result['first_name']}', second='{result['second_name']}'")
		print()

		if not passed:
			all_passed = False

	if all_passed:
		print("=" * 60)
		print("✓ All tests passed!")
	else:
		print("=" * 60)
		print("✗ Some tests failed")
