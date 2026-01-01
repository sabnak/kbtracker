"""
Extract and analyze the "crap" field value from all saves.
This appears around offset 0x50 in all decompressed data files.
"""
from pathlib import Path
import struct
import zlib
import hashlib


def decompress_save_file(save_path: Path) -> bytes:
	"""Decompress King's Bounty save data file."""
	with open(save_path, 'rb') as f:
		data = f.read()

	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	compressed_data = data[12:12+compressed_size]
	return zlib.decompress(compressed_data)


def extract_crap_field(data: bytes) -> tuple[int, bytes]:
	"""
	Extract the 'crap' field value.

	Format appears to be:
	- 4 bytes: field name length
	- N bytes: "crap" (field name)
	- 4 bytes: data length
	- M bytes: data
	"""
	# Find "crap" string
	crap_offset = data.find(b'crap')

	if crap_offset == -1:
		return -1, b''

	# The length is 4 bytes before "crap"
	name_length_offset = crap_offset - 4
	name_length = struct.unpack('<I', data[name_length_offset:name_length_offset+4])[0]

	# After "crap" should be the data length
	data_length_offset = crap_offset + 4
	data_length = struct.unpack('<I', data[data_length_offset:data_length_offset+4])[0]

	# Extract the data
	data_offset = data_length_offset + 4
	crap_data = data[data_offset:data_offset+data_length]

	return crap_offset, crap_data


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
	print("EXTRACTING 'CRAP' FIELD FROM ALL SAVES")
	print("=" * 80)

	crap_values = {}

	for name, path in saves.items():
		print(f"\n{name}: {path.parent.name}")
		print("-" * 80)

		data = decompress_save_file(path)
		offset, crap_data = extract_crap_field(data)

		crap_values[name] = crap_data

		print(f"  Offset: 0x{offset:08x} ({offset})")
		print(f"  Length: {len(crap_data)} bytes")
		print(f"  Hex: {crap_data.hex()}")

		# Calculate hash
		md5 = hashlib.md5(crap_data).hexdigest()
		sha1 = hashlib.sha1(crap_data).hexdigest()
		print(f"  MD5: {md5}")
		print(f"  SHA1: {sha1}")

		# Try to interpret as various types
		if len(crap_data) >= 4:
			val = struct.unpack('<I', crap_data[:4])[0]
			print(f"  First 4 bytes as uint32: {val} (0x{val:08x})")

		if len(crap_data) >= 8:
			val = struct.unpack('<Q', crap_data[:8])[0]
			print(f"  First 8 bytes as uint64: {val}")

	# Compare values
	print("\n" + "=" * 80)
	print("CAMPAIGN ID ANALYSIS")
	print("=" * 80)

	c1s1 = crap_values['C1S1']
	c1s2 = crap_values['C1S2']
	c2s1 = crap_values['C2S1']
	c2s2 = crap_values['C2S2']

	print("\nCampaign 1 Save 1:")
	print(f"  {c1s1.hex()}")

	print("\nCampaign 1 Save 2:")
	print(f"  {c1s2.hex()}")

	print("\nCampaign 2 Save 1:")
	print(f"  {c2s1.hex()}")

	print("\nCampaign 2 Save 2:")
	print(f"  {c2s2.hex()}")

	# Check if campaigns differ
	c1_same = (c1s1 == c1s2)
	c2_same = (c2s1 == c2s2)
	campaigns_differ = (c1s1 != c2s1)

	print("\nResults:")
	print(f"  Campaign 1 saves have same 'crap' value: {c1_same}")
	print(f"  Campaign 2 saves have same 'crap' value: {c2_same}")
	print(f"  Campaigns have different 'crap' values: {campaigns_differ}")

	if c1_same and c2_same and campaigns_differ:
		print("\n" + "=" * 80)
		print("*** CAMPAIGN ID FOUND IN 'CRAP' FIELD! ***")
		print("=" * 80)
		print(f"\n  Campaign 1 ID: {c1s1.hex()}")
		print(f"  Campaign 2 ID: {c2s1.hex()}")
	elif not c1_same or not c2_same:
		print("\n  'crap' field varies within campaigns - not a campaign ID")
		print("  This might be a random seed or session-specific data")


if __name__ == '__main__':
	main()
