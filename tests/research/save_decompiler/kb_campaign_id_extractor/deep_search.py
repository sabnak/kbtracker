"""
Deep search for campaign ID - search entire decompressed files.
"""
from pathlib import Path
import struct
import zlib


def decompress_save_file(save_path: Path) -> bytes:
	"""Decompress King's Bounty save data file."""
	with open(save_path, 'rb') as f:
		data = f.read()

	magic = data[0:4]
	if magic != b'slcb':
		raise ValueError(f"Invalid magic: {magic}")

	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	compressed_data = data[12:12+compressed_size]
	decompressed_data = zlib.decompress(compressed_data)

	return decompressed_data


def find_discriminating_regions(c1s1: bytes, c1s2: bytes, c2s1: bytes, c2s2: bytes) -> list[tuple[int, int]]:
	"""
	Find regions (not just single bytes) where campaigns differ.

	Returns: [(start_offset, length), ...]
	"""
	min_len = min(len(c1s1), len(c1s2), len(c2s1), len(c2s2))

	discriminating_regions = []
	in_region = False
	region_start = 0

	for offset in range(min_len):
		# Check if this byte is discriminating
		c1_same = (c1s1[offset] == c1s2[offset])
		c2_same = (c2s1[offset] == c2s2[offset])
		campaigns_differ = (c1s1[offset] != c2s1[offset]) if c1_same and c2_same else False

		if campaigns_differ:
			if not in_region:
				region_start = offset
				in_region = True
		else:
			if in_region:
				region_length = offset - region_start
				if region_length >= 4:  # Only report regions of 4+ bytes
					discriminating_regions.append((region_start, region_length))
				in_region = False

	return discriminating_regions


def main():
	"""Main search function."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	print("Loading and decompressing saves...")
	c1s1 = decompress_save_file(saves_dir / '1707078232' / 'data')
	c1s2 = decompress_save_file(saves_dir / '1707047253' / 'data')
	c2s1 = decompress_save_file(saves_dir / '1766864874' / 'data')
	c2s2 = decompress_save_file(saves_dir / '1767209722' / 'data')

	print(f"  C1S1: {len(c1s1):,} bytes")
	print(f"  C1S2: {len(c1s2):,} bytes")
	print(f"  C2S1: {len(c2s1):,} bytes")
	print(f"  C2S2: {len(c2s2):,} bytes")

	print("\nSearching for discriminating regions...")
	regions = find_discriminating_regions(c1s1, c1s2, c2s1, c2s2)

	print(f"\nFound {len(regions)} discriminating regions of 4+ bytes")

	if regions:
		print("\nFirst 50 regions:")
		for i, (offset, length) in enumerate(regions[:50]):
			print(f"\n  Region #{i+1}: Offset 0x{offset:08x} ({offset}), Length {length} bytes")

			# Show the data for each campaign
			c1_data = c1s1[offset:offset+min(length, 32)]
			c2_data = c2s1[offset:offset+min(length, 32)]

			print(f"    C1: {c1_data.hex()}")
			print(f"    C2: {c2_data.hex()}")

			# Try to interpret as integer if reasonable size
			if 4 <= length <= 8:
				if length == 4:
					c1_val = struct.unpack('<I', c1s1[offset:offset+4])[0]
					c2_val = struct.unpack('<I', c2s1[offset:offset+4])[0]
					print(f"    As uint32: C1={c1_val} (0x{c1_val:08x}), C2={c2_val} (0x{c2_val:08x})")
				elif length == 8:
					c1_val = struct.unpack('<Q', c1s1[offset:offset+8])[0]
					c2_val = struct.unpack('<Q', c2s1[offset:offset+8])[0]
					print(f"    As uint64: C1={c1_val}, C2={c2_val}")

			# Try to decode as string
			try:
				c1_str = c1_data.decode('utf-8')
				c2_str = c2_data.decode('utf-8')
				if c1_str.isprintable() and c2_str.isprintable():
					print(f"    As UTF-8: C1='{c1_str}', C2='{c2_str}'")
			except:
				pass

		# Look for promising candidates based on offset and size
		print("\n" + "=" * 80)
		print("MOST PROMISING CANDIDATES:")
		print("=" * 80)

		# Candidates likely to be campaign ID:
		# - Early in file (offset < 100,000)
		# - Standard size (4, 8, or 16 bytes)
		# - Has "reasonable" integer values

		promising = []
		for offset, length in regions:
			if offset < 100000 and length in [4, 8, 16]:
				promising.append((offset, length))

		for offset, length in promising[:20]:
			print(f"\nOffset 0x{offset:08x} ({offset}), {length} bytes:")

			if length == 4:
				c1_val = struct.unpack('<I', c1s1[offset:offset+4])[0]
				c2_val = struct.unpack('<I', c2s1[offset:offset+4])[0]
				c1_hex = c1s1[offset:offset+4].hex()
				c2_hex = c2s1[offset:offset+4].hex()
				print(f"  Campaign 1: {c1_val:10d} (0x{c1_val:08x})  hex:{c1_hex}")
				print(f"  Campaign 2: {c2_val:10d} (0x{c2_val:08x})  hex:{c2_hex}")

			elif length == 8:
				c1_val = struct.unpack('<Q', c1s1[offset:offset+8])[0]
				c2_val = struct.unpack('<Q', c2s1[offset:offset+8])[0]
				print(f"  Campaign 1: {c1_val}")
				print(f"  Campaign 2: {c2_val}")

			elif length == 16:
				c1_hex = c1s1[offset:offset+16].hex()
				c2_hex = c2s1[offset:offset+16].hex()
				print(f"  Campaign 1: {c1_hex}")
				print(f"  Campaign 2: {c2_hex}")


if __name__ == '__main__':
	main()
