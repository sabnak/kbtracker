"""
Search for campaign ID in decompressed DATA files.

Strategy:
1. Decompress all 4 data files
2. Search for unique identifiers near the beginning (likely in metadata section)
3. Find values that are identical within campaigns but differ between campaigns
"""
from pathlib import Path
import struct
import zlib


def decompress_save_file(save_path: Path) -> bytes:
	"""
	Decompress King's Bounty save data file.

	Format:
	- 4 bytes: Magic "slcb"
	- 4 bytes: Decompressed size (uint32 LE)
	- 4 bytes: Compressed size (uint32 LE)
	- N bytes: zlib compressed data
	"""
	with open(save_path, 'rb') as f:
		data = f.read()

	# Verify magic
	magic = data[0:4]
	if magic != b'slcb':
		raise ValueError(f"Invalid magic: {magic}")

	# Read sizes
	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	print(f"  Magic: {magic}")
	print(f"  Decompressed size: {decompressed_size:,} bytes")
	print(f"  Compressed size: {compressed_size:,} bytes")

	# Decompress
	compressed_data = data[12:12+compressed_size]
	decompressed_data = zlib.decompress(compressed_data)

	if len(decompressed_data) != decompressed_size:
		print(f"  WARNING: Size mismatch! Got {len(decompressed_data)}, expected {decompressed_size}")

	return decompressed_data


def search_for_strings(data: bytes, search_strings: list[str]) -> dict[str, list[int]]:
	"""Search for ASCII strings in binary data."""
	results = {}

	for search_str in search_strings:
		search_bytes = search_str.encode('utf-8')
		offsets = []

		offset = 0
		while True:
			pos = data.find(search_bytes, offset)
			if pos == -1:
				break
			offsets.append(pos)
			offset = pos + 1

		if offsets:
			results[search_str] = offsets

	return results


def find_header_fields(data: bytes, max_offset: int = 10000) -> None:
	"""Search for common field names in the header area."""
	print("\n  Searching for field names in first 10KB...")

	fields_to_search = [
		'ugid', 'cid', 'campaign', 'id', 'uid', 'guid', 'uuid',
		'game_id', 'campaign_id', 'session_id', 'save_id',
		'hero', 'player', 'name', 'session'
	]

	found = search_for_strings(data[:max_offset], fields_to_search)

	for field_name, offsets in found.items():
		print(f"    '{field_name}' found at offsets: {[f'0x{o:04x}' for o in offsets[:5]]}")


def extract_potential_ids(data: bytes, max_offset: int = 1000) -> list[tuple[int, any]]:
	"""
	Extract potential ID values from the header area.

	Look for:
	- 32-bit integers
	- 64-bit integers
	- Strings that look like IDs
	"""
	candidates = []

	# Check every 4-byte alignment for interesting uint32 values
	for offset in range(0, min(max_offset, len(data) - 8), 4):
		val32 = struct.unpack('<I', data[offset:offset+4])[0]
		val64 = struct.unpack('<Q', data[offset:offset+8])[0]

		# Look for "interesting" values (not too small, not too large)
		if 1000000 < val32 < 2000000000:
			candidates.append((offset, 'uint32', val32))

		if 1000000000000 < val64 < 2000000000000:
			candidates.append((offset, 'uint64', val64))

	return candidates


def main():
	"""Main analysis function."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	saves = {
		'C1S1': saves_dir / '1707078232' / 'data',
		'C1S2': saves_dir / '1707047253' / 'data',
		'C2S1': saves_dir / '1766864874' / 'data',
		'C2S2': saves_dir / '1767209722' / 'data',
	}

	print("=" * 80)
	print("DECOMPRESSING DATA FILES")
	print("=" * 80)

	decompressed = {}

	for name, path in saves.items():
		print(f"\n{name}: {path.parent.name}")
		print("-" * 80)
		try:
			data = decompress_save_file(path)
			decompressed[name] = data
			print(f"  [OK] Decompressed: {len(data):,} bytes")

			# Search for field names
			find_header_fields(data)

		except Exception as e:
			print(f"  [ERROR] {e}")

	# Compare headers
	print("\n" + "=" * 80)
	print("COMPARING FIRST 1000 BYTES OF DECOMPRESSED DATA")
	print("=" * 80)

	# Show hex dumps of first 256 bytes
	for name in ['C1S1', 'C1S2', 'C2S1', 'C2S2']:
		if name in decompressed:
			print(f"\n{name} (first 256 bytes):")
			data = decompressed[name][:256]
			for i in range(0, len(data), 16):
				hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
				ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
				print(f'  {i:04x}  {hex_part:<48}  {ascii_part}')

	# Find discriminating bytes in headers
	print("\n" + "=" * 80)
	print("FINDING CAMPAIGN ID IN HEADERS")
	print("=" * 80)

	if len(decompressed) == 4:
		c1s1 = decompressed['C1S1'][:1000]
		c1s2 = decompressed['C1S2'][:1000]
		c2s1 = decompressed['C2S1'][:1000]
		c2s2 = decompressed['C2S2'][:1000]

		# Find bytes that are identical within campaigns
		min_len = min(len(c1s1), len(c1s2), len(c2s1), len(c2s2))

		discriminating = []
		for offset in range(min_len):
			# Check if Campaign 1 saves have same byte
			if c1s1[offset] == c1s2[offset]:
				c1_val = c1s1[offset]

				# Check if Campaign 2 saves have same byte
				if c2s1[offset] == c2s2[offset]:
					c2_val = c2s1[offset]

					# Check if campaigns differ
					if c1_val != c2_val:
						discriminating.append(offset)

		print(f"\nFound {len(discriminating)} discriminating bytes in first {min_len} bytes")

		if discriminating:
			print("\nFirst 20 discriminating offsets:")
			for i, offset in enumerate(discriminating[:20]):
				c1_val = c1s1[offset]
				c2_val = c2s1[offset]
				print(f"  0x{offset:04x} ({offset:4d}): C1=0x{c1_val:02x} ({c1_val:3d}), C2=0x{c2_val:02x} ({c2_val:3d})")

			# Look for 32-bit integer candidates
			print("\nChecking 32-bit integer candidates:")
			for offset in discriminating:
				if offset + 4 <= min_len:
					c1_val = struct.unpack('<I', c1s1[offset:offset+4])[0]
					c2_val = struct.unpack('<I', c2s1[offset:offset+4])[0]

					# Only show if both values are in reasonable range
					if 100 < c1_val < 2147483647 and 100 < c2_val < 2147483647:
						print(f"  0x{offset:04x}: C1={c1_val} (0x{c1_val:08x}), C2={c2_val} (0x{c2_val:08x})")


if __name__ == '__main__':
	main()
