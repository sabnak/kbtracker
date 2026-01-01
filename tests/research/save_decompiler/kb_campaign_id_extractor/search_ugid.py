"""
Search for ugid and other ID-like fields in decompressed data.
"""
from pathlib import Path
import struct
import zlib


def decompress_save_file(save_path: Path) -> bytes:
	"""Decompress King's Bounty save data file."""
	with open(save_path, 'rb') as f:
		data = f.read()

	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	compressed_data = data[12:12+compressed_size]
	return zlib.decompress(compressed_data)


def search_field_with_value(data: bytes, field_name: str, max_search: int = 500000) -> list[tuple[int, bytes]]:
	"""
	Search for a field name and extract the value that follows.

	Returns: [(offset, value_bytes), ...]
	"""
	results = []
	field_bytes = field_name.encode('utf-8')

	offset = 0
	while offset < max_search:
		pos = data.find(field_bytes, offset)
		if pos == -1:
			break

		# Try to extract value after field name
		# Assume format: [field_name]\x00[4_byte_length][value_data]
		value_offset = pos + len(field_bytes)

		# Skip null terminator if present
		if value_offset < len(data) and data[value_offset] == 0:
			value_offset += 1

		# Try to read length and value
		if value_offset + 4 <= len(data):
			value_length = struct.unpack('<I', data[value_offset:value_offset+4])[0]

			if 0 < value_length < 1000:  # Reasonable length
				value_data = data[value_offset+4:value_offset+4+value_length]
				if len(value_data) == value_length:
					results.append((pos, value_data))

		offset = pos + 1

	return results


def main():
	"""Main search function."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	saves = {
		'C1S1': saves_dir / '1707078232' / 'data',
		'C1S2': saves_dir / '1707047253' / 'data',
		'C2S1': saves_dir / '1766864874' / 'data',
		'C2S2': saves_dir / '1767209722' / 'data',
	}

	print("=" * 80)
	print("SEARCHING FOR CAMPAIGN ID FIELDS")
	print("=" * 80)

	# Fields to search
	field_names = ['ugid', 'guid', 'uuid', 'cid', 'campaign_id', 'session_id', 'game_id', 'save_id']

	decompressed = {}
	for name, path in saves.items():
		print(f"\nLoading {name}...")
		decompressed[name] = decompress_save_file(path)
		print(f"  Size: {len(decompressed[name]):,} bytes")

	for field_name in field_names:
		print(f"\n{'=' * 80}")
		print(f"Searching for field: '{field_name}'")
		print(f"{'=' * 80}")

		all_results = {}
		for name in ['C1S1', 'C1S2', 'C2S1', 'C2S2']:
			results = search_field_with_value(decompressed[name], field_name)
			all_results[name] = results

			if results:
				print(f"\n{name}: Found {len(results)} occurrences")
				for i, (offset, value) in enumerate(results[:3]):
					print(f"  Occurrence #{i+1} at offset 0x{offset:08x}:")
					print(f"    Hex: {value.hex()}")

					# Try to interpret
					if len(value) == 4:
						val = struct.unpack('<I', value)[0]
						print(f"    As uint32: {val} (0x{val:08x})")
					elif len(value) == 8:
						val = struct.unpack('<Q', value)[0]
						print(f"    As uint64: {val}")
					elif len(value) == 16:
						print(f"    As UUID: {value.hex()}")

					try:
						s = value.decode('utf-8')
						if s.isprintable():
							print(f"    As UTF-8: '{s}'")
					except:
						pass

		# Check if this field could be campaign ID
		if any(all_results.values()):
			print(f"\n  {'ANALYSIS':=^76}")

			# Get first occurrence from each save
			values = {}
			for name in ['C1S1', 'C1S2', 'C2S1', 'C2S2']:
				if all_results[name]:
					values[name] = all_results[name][0][1]

			if len(values) == 4:
				c1s1_val = values['C1S1']
				c1s2_val = values['C1S2']
				c2s1_val = values['C2S1']
				c2s2_val = values['C2S2']

				print(f"  Campaign 1 Save 1: {c1s1_val.hex()}")
				print(f"  Campaign 1 Save 2: {c1s2_val.hex()}")
				print(f"  Campaign 2 Save 1: {c2s1_val.hex()}")
				print(f"  Campaign 2 Save 2: {c2s2_val.hex()}")

				c1_match = (c1s1_val == c1s2_val)
				c2_match = (c2s1_val == c2s2_val)
				campaigns_differ = (c1s1_val != c2s1_val)

				print(f"\n  Campaign 1 saves match: {c1_match}")
				print(f"  Campaign 2 saves match: {c2_match}")
				print(f"  Campaigns differ: {campaigns_differ}")

				if c1_match and c2_match and campaigns_differ:
					print(f"\n  *** POTENTIAL CAMPAIGN ID FOUND! ***")


if __name__ == '__main__':
	main()
