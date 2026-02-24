"""
Analyze patterns around items to understand inventory structure
"""
import re
import struct
from pathlib import Path
from collections import defaultdict

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def find_all_length_prefixed_ascii(
	data: bytes,
	min_length: int = 3,
	max_length: int = 100
) -> list[tuple[int, str, bytes]]:
	"""
	Find all length-prefixed ASCII strings that look like item kb_ids

	:param data:
		Decompressed save data
	:param min_length:
		Minimum string length
	:param max_length:
		Maximum string length
	:return:
		List of (position, string, next_8_bytes) tuples
	"""
	results = []
	pos = 0

	while pos < len(data) - 8:
		if pos + 4 > len(data):
			break

		try:
			length = struct.unpack('<I', data[pos:pos+4])[0]

			if min_length <= length <= max_length:
				if pos + 4 + length > len(data):
					pos += 1
					continue

				try:
					string = data[pos+4:pos+4+length].decode('ascii', errors='strict')

					# Check if it looks like an item ID
					if re.match(r'^[a-z][a-z0-9_]*$', string):
						next_bytes = data[pos+4+length:pos+4+length+8] if pos+4+length+8 <= len(data) else b''
						results.append((pos, string, next_bytes))
				except:
					pass
		except:
			pass

		pos += 1

	return results


def analyze_quantity_patterns(items: list[tuple[int, str, bytes]]) -> None:
	"""
	Analyze patterns in bytes following item names to identify quantity encoding

	:param items:
		List of (position, item_name, next_bytes) tuples
	"""
	print("\n=== Quantity Pattern Analysis ===")

	# Group by pattern type
	patterns = defaultdict(list)

	for pos, name, next_bytes in items:
		if len(next_bytes) >= 4:
			# Check if next 4 bytes could be a quantity (uint32)
			try:
				quantity = struct.unpack('<I', next_bytes[:4])[0]
				if 0 < quantity < 10000:
					patterns['direct_uint32'].append((pos, name, quantity))
			except:
				pass

			# Check for slruck metadata pattern
			if b'slruck' in next_bytes:
				patterns['slruck_metadata'].append((pos, name, next_bytes.hex()))

			# Check for other metadata keywords
			metadata_keywords = [b'count', b'flags', b'lvars', b'id', b'strg']
			for keyword in metadata_keywords:
				if keyword in next_bytes:
					patterns[f'metadata_{keyword.decode()}'].append((pos, name, next_bytes.hex()))

	# Display patterns
	for pattern_type, entries in patterns.items():
		print(f"\n{pattern_type}: {len(entries)} occurrences")
		for pos, name, data in entries[:10]:
			print(f"  Pos {pos:8d}: {name:30s} -> {data}")


def find_sections_before_items(
	data: bytes,
	items: list[tuple[int, str, bytes]]
) -> None:
	"""
	Find section markers that appear before item names

	:param data:
		Decompressed save data
	:param items:
		List of (position, item_name, next_bytes) tuples
	"""
	print("\n=== Sections Before Items ===")

	section_markers = [
		b'.garrison',
		b'.items',
		b'.spells',
		b'.shopunits',
		b'.temp',
		b'.hero',
		b'.inventory',
		b'.equipment',
		b'.backpack',
	]

	# For each item, find the nearest section marker before it
	section_counts = defaultdict(int)

	for pos, name, _ in items[:100]:  # Analyze first 100 items
		search_start = max(0, pos - 5000)
		chunk = data[search_start:pos]

		closest_marker = None
		closest_distance = float('inf')

		for marker in section_markers:
			marker_pos = chunk.rfind(marker)
			if marker_pos != -1:
				distance = len(chunk) - marker_pos
				if distance < closest_distance:
					closest_distance = distance
					closest_marker = marker

		if closest_marker:
			section_counts[closest_marker.decode('ascii')] += 1

	print("\nSection marker frequency before items:")
	for marker, count in sorted(section_counts.items(), key=lambda x: -x[1]):
		print(f"  {marker:20s}: {count:4d} items")


def find_clusters(items: list[tuple[int, str, bytes]], max_gap: int = 1000) -> list[list[tuple[int, str, bytes]]]:
	"""
	Group items into clusters based on proximity

	:param items:
		List of (position, item_name, next_bytes) tuples
	:param max_gap:
		Maximum gap between items in same cluster
	:return:
		List of item clusters
	"""
	if not items:
		return []

	sorted_items = sorted(items, key=lambda x: x[0])
	clusters = []
	current_cluster = [sorted_items[0]]

	for item in sorted_items[1:]:
		if item[0] - current_cluster[-1][0] <= max_gap:
			current_cluster.append(item)
		else:
			clusters.append(current_cluster)
			current_cluster = [item]

	if current_cluster:
		clusters.append(current_cluster)

	return clusters


def analyze_clusters(data: bytes, items: list[tuple[int, str, bytes]]) -> None:
	"""
	Analyze item clusters to identify inventory sections

	:param data:
		Decompressed save data
	:param items:
		List of (position, item_name, next_bytes) tuples
	"""
	print("\n=== Item Clusters Analysis ===")

	clusters = find_clusters(items, max_gap=2000)

	print(f"\nFound {len(clusters)} item clusters")

	for i, cluster in enumerate(clusters[:20]):  # Show first 20 clusters
		start_pos = cluster[0][0]
		end_pos = cluster[-1][0]
		item_names = [name for _, name, _ in cluster]

		# Find section marker before cluster
		search_start = max(0, start_pos - 5000)
		chunk = data[search_start:start_pos]

		section_markers = [b'.garrison', b'.items', b'.spells', b'.shopunits', b'.temp']
		closest_marker = None

		for marker in section_markers:
			marker_pos = chunk.rfind(marker)
			if marker_pos != -1:
				if closest_marker is None or marker_pos > closest_marker[1]:
					closest_marker = (marker.decode('ascii'), marker_pos)

		marker_name = closest_marker[0] if closest_marker else "unknown"

		print(f"\nCluster {i+1}: {len(cluster)} items ({start_pos} - {end_pos})")
		print(f"  Section: {marker_name}")
		print(f"  Items: {', '.join(item_names[:10])}{'...' if len(item_names) > 10 else ''}")


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	print(f"Decompressed save file size: {len(data)} bytes")

	# Find all potential item kb_ids
	print("\nScanning for length-prefixed ASCII strings...")
	items = find_all_length_prefixed_ascii(data)
	print(f"Found {len(items)} potential item kb_ids")

	# Analyze patterns
	analyze_quantity_patterns(items)
	find_sections_before_items(data, items)
	analyze_clusters(data, items)
