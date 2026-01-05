"""
Analyze actual byte lengths of shop IDs in UTF-16-LE encoding
to determine if 200-byte overlap is sufficient
"""
from pathlib import Path
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
import re


def analyze_shop_id_byte_lengths():
	"""
	Analyze byte lengths of shop IDs to verify overlap size

	Determines if 200-byte overlap is sufficient by measuring
	actual UTF-16-LE encoded lengths of shop IDs in save files.
	"""
	decompressor = SaveFileDecompressor()
	save_path = Path("/app/tests/game_files/saves/1707047253/data")

	if not save_path.exists():
		print(f"ERROR: Save file not found: {save_path}")
		return

	data = decompressor.decompress(save_path)

	pos = 0
	shop_ids_found = set()

	while pos < len(data):
		chunk_size = 50000
		if pos + chunk_size > len(data):
			chunk_size = len(data) - pos

		try:
			text = data[pos:pos+chunk_size].decode('utf-16-le', errors='ignore')
			matches = re.finditer(r'itext_([-\w]+)_(\d+)', text)

			for match in matches:
				shop_id_full = match.group(0)
				shop_ids_found.add(shop_id_full)
		except:
			pass

		pos += chunk_size

	byte_lengths = []
	for shop_id in shop_ids_found:
		byte_length = len(shop_id.encode('utf-16-le'))
		byte_lengths.append((shop_id, byte_length))

	byte_lengths.sort(key=lambda x: x[1], reverse=True)

	print("=" * 80)
	print("SHOP ID BYTE LENGTH ANALYSIS (UTF-16-LE)")
	print("=" * 80)
	print()
	print(f"Total unique shop IDs: {len(byte_lengths)}")
	print(f"Minimum byte length: {min(byte_lengths, key=lambda x: x[1])[1]} bytes")
	print(f"Maximum byte length: {max(byte_lengths, key=lambda x: x[1])[1]} bytes")
	print(f"Average byte length: {sum(x[1] for x in byte_lengths) / len(byte_lengths):.1f} bytes")
	print()

	print("Top 10 longest shop IDs:")
	print("-" * 80)
	for shop_id, byte_len in byte_lengths[:10]:
		print(f"  {shop_id:45s} = {byte_len:3d} bytes")

	print()
	print("-" * 80)
	print("OVERLAP SUFFICIENCY ANALYSIS:")
	print("-" * 80)

	max_length = max(byte_lengths, key=lambda x: x[1])[1]
	current_overlap = 200
	safety_margin = current_overlap / max_length

	print(f"Current overlap: {current_overlap} bytes")
	print(f"Longest shop ID: {max_length} bytes")
	print(f"Safety margin: {safety_margin:.1f}x")
	print()

	if safety_margin >= 3.0:
		print("✓ EXCELLENT: 200-byte overlap provides 3x+ safety margin")
	elif safety_margin >= 2.0:
		print("✓ GOOD: 200-byte overlap provides 2x+ safety margin")
	elif safety_margin >= 1.5:
		print("⚠ ACCEPTABLE: 200-byte overlap is sufficient but conservative increase recommended")
	else:
		print("✗ INSUFFICIENT: Overlap should be increased")

	recommended = max_length * 3
	recommended = ((recommended + 99) // 100) * 100

	print()
	print(f"Recommended overlap for 3x safety: {recommended} bytes")


if __name__ == "__main__":
	analyze_shop_id_byte_lengths()
