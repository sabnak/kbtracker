"""
Search for GUID/UUID-like patterns (128-bit unique IDs) in save files.
These are often used as campaign/session identifiers.
"""
from pathlib import Path
import struct
import zlib
import uuid


def decompress_save_file(save_path: Path) -> bytes:
	"""Decompress King's Bounty save data file."""
	with open(save_path, 'rb') as f:
		data = f.read()

	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	compressed_data = data[12:12+compressed_size]
	return zlib.decompress(compressed_data)


def find_guid_candidates(data: bytes, max_offset: int = 100000) -> list[tuple[int, bytes]]:
	"""
	Find potential GUID/UUID values (128-bit = 16 bytes).

	Look for 16-byte sequences that:
	- Appear in standard GUID format areas
	- Have reasonable entropy (not all zeros or all same byte)
	"""
	candidates = []

	# Check every offset for 16-byte values
	for offset in range(0, min(max_offset, len(data) - 16)):
		chunk = data[offset:offset+16]

		# Check if it looks like a GUID (has some variety, not all zeros)
		unique_bytes = len(set(chunk))

		if unique_bytes >= 8:  # At least 8 different byte values
			candidates.append((offset, chunk))

	return candidates


def main():
	"""Main function."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	saves = {
		'C1S1': saves_dir / '1707078232' / 'data',
		'C1S2': saves_dir / '1707047253' / 'data',
		'C2S1': saves_dir / '1766864874' / 'data',
		'C2S2': saves_dir / '1767209722' / 'data',
	}

	print("=" * 80)
	print("SEARCHING FOR GUID/UUID PATTERNS")
	print("=" * 80)

	all_candidates = {}

	for name, path in saves.items():
		print(f"\n{name}: {path.parent.name}")
		print("-" * 80)

		data = decompress_save_file(path)
		candidates = find_guid_candidates(data, max_offset=50000)

		all_candidates[name] = candidates

		print(f"  Found {len(candidates)} potential GUID candidates in first 50KB")

	# Now find GUIDs that are:
	# 1. Present at same offset in all 4 files
	# 2. Same within each campaign
	# 3. Different between campaigns

	print("\n" + "=" * 80)
	print("LOOKING FOR CAMPAIGN ID GUIDS")
	print("=" * 80)

	# Get offsets that appear in all 4 saves
	c1s1_offsets = set(o for o, _ in all_candidates['C1S1'])
	c1s2_offsets = set(o for o, _ in all_candidates['C1S2'])
	c2s1_offsets = set(o for o, _ in all_candidates['C2S1'])
	c2s2_offsets = set(o for o, _ in all_candidates['C2S2'])

	common_offsets = c1s1_offsets & c1s2_offsets & c2s1_offsets & c2s2_offsets

	print(f"\nFound {len(common_offsets)} offsets with GUID candidates in all 4 saves")

	# Build lookup dicts
	c1s1_dict = {o: v for o, v in all_candidates['C1S1']}
	c1s2_dict = {o: v for o, v in all_candidates['C1S2']}
	c2s1_dict = {o: v for o, v in all_candidates['C2S1']}
	c2s2_dict = {o: v for o, v in all_candidates['C2S2']}

	campaign_id_candidates = []

	for offset in sorted(common_offsets):
		c1s1_guid = c1s1_dict[offset]
		c1s2_guid = c1s2_dict[offset]
		c2s1_guid = c2s1_dict[offset]
		c2s2_guid = c2s2_dict[offset]

		# Check if this could be campaign ID
		c1_same = (c1s1_guid == c1s2_guid)
		c2_same = (c2s1_guid == c2s2_guid)
		campaigns_differ = (c1s1_guid != c2s1_guid)

		if c1_same and c2_same and campaigns_differ:
			campaign_id_candidates.append((offset, c1s1_guid, c2s1_guid))

	print(f"\n*** FOUND {len(campaign_id_candidates)} CAMPAIGN ID CANDIDATES! ***")

	if campaign_id_candidates:
		print("\nCampaign ID Candidates:")
		for offset, c1_guid, c2_guid in campaign_id_candidates[:10]:
			print(f"\n  Offset 0x{offset:08x} ({offset}):")
			print(f"    Campaign 1: {c1_guid.hex()}")
			print(f"    Campaign 2: {c2_guid.hex()}")

			# Try to format as standard GUID
			try:
				c1_uuid = uuid.UUID(bytes=c1_guid)
				c2_uuid = uuid.UUID(bytes=c2_guid)
				print(f"    Campaign 1 (UUID): {c1_uuid}")
				print(f"    Campaign 2 (UUID): {c2_uuid}")
			except:
				pass

			# Try little-endian interpretation
			c1_int1 = struct.unpack('<Q', c1_guid[:8])[0]
			c1_int2 = struct.unpack('<Q', c1_guid[8:])[0]
			c2_int1 = struct.unpack('<Q', c2_guid[:8])[0]
			c2_int2 = struct.unpack('<Q', c2_guid[8:])[0]

			print(f"    Campaign 1 (2x uint64): {c1_int1}, {c1_int2}")
			print(f"    Campaign 2 (2x uint64): {c2_int1}, {c2_int2}")


if __name__ == '__main__':
	main()
