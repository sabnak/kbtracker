"""
Quick script to find campaign identifier by comparing save info files.

Strategy:
1. Compare Campaign 1 saves - find bytes that are IDENTICAL
2. Compare Campaign 2 saves - find bytes that are IDENTICAL
3. Find offsets where Campaign 1 and Campaign 2 have DIFFERENT values
4. Extract and display campaign ID candidates
"""
from pathlib import Path
import struct


def read_binary(file_path: Path) -> bytes:
	"""Read file as binary data."""
	with open(file_path, 'rb') as f:
		return f.read()


def find_invariant_bytes(data1: bytes, data2: bytes) -> dict[int, int]:
	"""
	Find byte offsets where both files have the same value.

	Returns: {offset: byte_value} for identical bytes
	"""
	min_len = min(len(data1), len(data2))
	invariant = {}

	for offset in range(min_len):
		if data1[offset] == data2[offset]:
			invariant[offset] = data1[offset]

	return invariant


def find_discriminating_offsets(
	campaign1_invariant: dict[int, int],
	campaign2_invariant: dict[int, int]
) -> list[int]:
	"""
	Find offsets where both campaigns have invariant bytes,
	but the values differ between campaigns.
	"""
	discriminating = []

	for offset in campaign1_invariant:
		if offset in campaign2_invariant:
			if campaign1_invariant[offset] != campaign2_invariant[offset]:
				discriminating.append(offset)

	return discriminating


def extract_candidates(data: bytes, offset: int) -> dict[str, any]:
	"""Extract various interpretations of data at offset."""
	candidates = {
		'offset': f'0x{offset:04x}',
		'byte': f'0x{data[offset]:02x}',
	}

	# Try 32-bit integer
	if offset + 4 <= len(data):
		val = struct.unpack('<I', data[offset:offset+4])[0]
		candidates['uint32_le'] = f'0x{val:08x}'

	# Try 64-bit integer
	if offset + 8 <= len(data):
		val = struct.unpack('<Q', data[offset:offset+8])[0]
		candidates['uint64_le'] = f'0x{val:016x}'

	# Try 16-byte chunk (UUID-like)
	if offset + 16 <= len(data):
		chunk = data[offset:offset+16].hex()
		candidates['16_bytes'] = chunk

	return candidates


def main():
	"""Main analysis function."""
	# File paths
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	campaign1_save1 = saves_dir / '1707078232' / 'info'
	campaign1_save2 = saves_dir / '1707047253' / 'info'
	campaign2_save1 = saves_dir / '1766864874' / 'info'
	campaign2_save2 = saves_dir / '1767209722' / 'info'

	print("=" * 80)
	print("CAMPAIGN IDENTIFIER SEARCH")
	print("=" * 80)

	# Read all files
	print("\n[1/4] Reading save files...")
	c1s1_data = read_binary(campaign1_save1)
	c1s2_data = read_binary(campaign1_save2)
	c2s1_data = read_binary(campaign2_save1)
	c2s2_data = read_binary(campaign2_save2)

	print(f"  Campaign 1 Save 1: {len(c1s1_data):,} bytes")
	print(f"  Campaign 1 Save 2: {len(c1s2_data):,} bytes")
	print(f"  Campaign 2 Save 1: {len(c2s1_data):,} bytes")
	print(f"  Campaign 2 Save 2: {len(c2s2_data):,} bytes")

	# Find invariant bytes within each campaign
	print("\n[2/4] Finding invariant bytes within campaigns...")
	c1_invariant = find_invariant_bytes(c1s1_data, c1s2_data)
	c2_invariant = find_invariant_bytes(c2s1_data, c2s2_data)

	print(f"  Campaign 1: {len(c1_invariant):,} invariant bytes")
	print(f"  Campaign 2: {len(c2_invariant):,} invariant bytes")

	# Find discriminating offsets
	print("\n[3/4] Finding discriminating bytes between campaigns...")
	discriminating = find_discriminating_offsets(c1_invariant, c2_invariant)

	print(f"  Found {len(discriminating):,} discriminating offsets")

	# Extract candidates
	print("\n[4/4] Extracting campaign ID candidates...")
	print("\n" + "=" * 80)
	print("CAMPAIGN ID CANDIDATES")
	print("=" * 80)

	# Show first 20 candidates
	for i, offset in enumerate(discriminating[:20]):
		print(f"\n--- Candidate #{i+1} at offset 0x{offset:04x} ({offset}) ---")

		c1_val = c1_invariant[offset]
		c2_val = c2_invariant[offset]

		print(f"  Campaign 1 byte: 0x{c1_val:02x} ({c1_val})")
		print(f"  Campaign 2 byte: 0x{c2_val:02x} ({c2_val})")

		# Show 32-bit interpretation
		if offset + 4 <= len(c1s1_data):
			c1_u32 = struct.unpack('<I', c1s1_data[offset:offset+4])[0]
			c2_u32 = struct.unpack('<I', c2s1_data[offset:offset+4])[0]
			print(f"  As uint32: C1=0x{c1_u32:08x}, C2=0x{c2_u32:08x}")

	if len(discriminating) > 20:
		print(f"\n... and {len(discriminating) - 20} more candidates")

	# Look for clusters (consecutive discriminating bytes)
	print("\n" + "=" * 80)
	print("LOOKING FOR CLUSTERS (consecutive discriminating bytes)")
	print("=" * 80)

	clusters = []
	if discriminating:
		cluster_start = discriminating[0]
		cluster_len = 1

		for i in range(1, len(discriminating)):
			if discriminating[i] == discriminating[i-1] + 1:
				cluster_len += 1
			else:
				if cluster_len >= 4:  # At least 4 consecutive bytes
					clusters.append((cluster_start, cluster_len))
				cluster_start = discriminating[i]
				cluster_len = 1

		if cluster_len >= 4:
			clusters.append((cluster_start, cluster_len))

	if clusters:
		print(f"\nFound {len(clusters)} clusters of 4+ consecutive bytes:")
		for start, length in clusters[:10]:
			print(f"\n  Offset 0x{start:04x} ({start}), length {length} bytes:")

			# Show as 32-bit int if length >= 4
			if length >= 4:
				c1_val = struct.unpack('<I', c1s1_data[start:start+4])[0]
				c2_val = struct.unpack('<I', c2s1_data[start:start+4])[0]
				print(f"    Campaign 1 (uint32): 0x{c1_val:08x} ({c1_val})")
				print(f"    Campaign 2 (uint32): 0x{c2_val:08x} ({c2_val})")

			# Show as 64-bit int if length >= 8
			if length >= 8:
				c1_val = struct.unpack('<Q', c1s1_data[start:start+8])[0]
				c2_val = struct.unpack('<Q', c2s1_data[start:start+8])[0]
				print(f"    Campaign 1 (uint64): 0x{c1_val:016x}")
				print(f"    Campaign 2 (uint64): 0x{c2_val:016x}")
	else:
		print("\nNo clusters found - campaign ID is likely a single value")

	print("\n" + "=" * 80)
	print("ANALYSIS COMPLETE")
	print("=" * 80)


if __name__ == '__main__':
	main()
