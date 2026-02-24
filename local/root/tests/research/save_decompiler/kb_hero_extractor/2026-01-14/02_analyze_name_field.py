"""
Analyze info file structure to find hero name field
"""
from pathlib import Path
import struct


SAMPLES_DIR = Path(__file__).parent / "tmp"


def analyze_info_file(info_path: Path) -> None:
	"""
	Analyze info file to find name field structure

	:param info_path:
		Path to info file binary
	"""
	print()
	print("=" * 70)
	print(f"File: {info_path.name}")
	print("=" * 70)

	data = info_path.read_bytes()
	print(f"File size: {len(data)} bytes")

	# Find all occurrences of "name"
	name_marker = b"name"
	occurrences = []
	pos = 0

	while pos < len(data):
		pos = data.find(name_marker, pos)
		if pos == -1:
			break
		occurrences.append(pos)
		pos += 1

	print(f"Found {len(occurrences)} occurrences of 'name' marker")

	# Analyze first 3 occurrences
	for i, pos in enumerate(occurrences[:3]):
		print()
		print(f"--- Occurrence {i+1} at offset {pos} ---")

		# Show context
		start = max(0, pos - 30)
		end = min(len(data), pos + 150)
		context = data[start:end]

		print(f"Context bytes: {context[:80]}...")
		print(f"Context text:  {context.decode('ascii', errors='replace')[:100]}")

		# Check for length prefix before "name"
		if pos >= 4:
			len_before = struct.unpack("<I", data[pos-4:pos])[0]
			print(f"Uint32 BEFORE 'name': {len_before} (0x{len_before:08x})")

		# Check for length after "name" (next 4 bytes)
		if pos + 4 + 4 <= len(data):
			len_after = struct.unpack("<I", data[pos+4:pos+8])[0]
			print(f"Uint32 AFTER 'name':  {len_after} (0x{len_after:08x})")

			# Try to read string at that length
			if 1 <= len_after <= 100 and pos + 8 + len_after <= len(data):
				string_data = data[pos+8:pos+8+len_after]

				# Try UTF-8
				try:
					string_utf8 = string_data.decode("utf-8", errors="strict")
					print(f"  → UTF-8 string: '{string_utf8}'")
					continue
				except:
					pass

				# Try UTF-16LE
				try:
					string_utf16 = string_data.decode("utf-16-le", errors="strict")
					print(f"  → UTF-16LE string: '{string_utf16}'")
					continue
				except:
					pass

				# Show raw bytes
				print(f"  → Raw bytes: {string_data[:50]}")


if __name__ == "__main__":
	print("Analyzing info file structure...")

	for info_file in sorted(SAMPLES_DIR.glob("*.bin")):
		analyze_info_file(info_file)

	print()
	print("=" * 70)
	print("Analysis complete!")
