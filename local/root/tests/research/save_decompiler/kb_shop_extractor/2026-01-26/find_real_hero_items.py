"""
Search for actual hero inventory items from screenshot
"""
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def search_for_items(data: bytes, item_names: list[str]) -> dict[str, list[int]]:
	"""
	Search for specific item names in save data

	:param data:
		Decompressed save data
	:param item_names:
		List of item kb_ids to search for
	:return:
		Dict mapping item name to list of positions
	"""
	results = {}

	for item_name in item_names:
		item_bytes = item_name.encode('ascii')
		positions = []

		pos = 0
		while pos < len(data):
			pos = data.find(item_bytes, pos)
			if pos == -1:
				break
			positions.append(pos)
			pos += 1

		if positions:
			results[item_name] = positions

	return results


def analyze_item_cluster(data: bytes, positions: list[int]) -> None:
	"""
	Analyze if items are clustered together

	:param data:
		Decompressed save data
	:param positions:
		List of item positions to analyze
	"""
	if not positions:
		return

	sorted_pos = sorted(positions)
	print(f"\nItem positions range: {sorted_pos[0]} to {sorted_pos[-1]}")
	print(f"Total span: {sorted_pos[-1] - sorted_pos[0]} bytes")

	# Check for clusters (items within 10000 bytes of each other)
	clusters = []
	current_cluster = [sorted_pos[0]]

	for pos in sorted_pos[1:]:
		if pos - current_cluster[-1] <= 10000:
			current_cluster.append(pos)
		else:
			clusters.append(current_cluster)
			current_cluster = [pos]

	if current_cluster:
		clusters.append(current_cluster)

	print(f"\nFound {len(clusters)} cluster(s):")
	for i, cluster in enumerate(clusters, 1):
		start, end = cluster[0], cluster[-1]
		print(f"  Cluster {i}: {len(cluster)} items, range {start}-{end} (span: {end-start} bytes)")


def find_section_before_position(data: bytes, pos: int, distance: int = 5000) -> None:
	"""
	Find section markers before a position

	:param data:
		Decompressed save data
	:param pos:
		Position to search before
	:param distance:
		Distance to search backwards
	"""
	start = max(0, pos - distance)
	chunk = data[start:pos]

	markers = [
		b'.items',
		b'.ehero',
		b'.hero',
		b'.inventory',
		b'.backpack',
		b'.castleruler1',
		b'.actors',
	]

	print(f"\n  Section markers within {distance} bytes before position {pos}:")
	for marker in markers:
		marker_pos = chunk.rfind(marker)
		if marker_pos != -1:
			abs_pos = start + marker_pos
			distance_to_item = pos - abs_pos
			print(f"    {marker.decode('ascii'):20s} at {abs_pos:8d} (distance: {distance_to_item:5d} bytes)")


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	print(f"Decompressed save file size: {len(data)} bytes\n")

	# Actual hero inventory items from screenshot (>200 total items)
	inventory_items = [
		"addon3_magic_ingridients",
		"kerus_sword",
		"addon4_human_battle_mage_braces",
		"flame_necklace",
		"addon4_demon_pandemonic_gloves",
		"addon4_spell_rock_holy_rain_100",
		"addon4_spell_rock_resurrection_80",
		"addon4_spell_rock_life_stealer_100",
		"addon4_spell_rock_fire_shield_200",
		"addon4_turtle_shield",
		"addon3_shield_tristrem_founder",
		"addon3_quest_hobo",
		"addon3_quest_baron_ponton",
		"addon3_quest_weapon_cargo",
		"addon3_quest_pow",
	]

	# Hero equipped items
	hero_equipped = [
		"battlemage_helm",
		"pictures_book",
		"addon4_human_archmage_boots",
		"addon4_neutral_beholder_amulet_3",
		"addon4_elf_poison_staff",
	]

	# Companion 1 equipped items
	companion1_equipped = [
		"arhmage_staff",
		"destructor_gloves",
		"sword_full_moon",
		"wizard_mantle",
	]

	# Companion 2 equipped items
	companion2_equipped = [
		"addon4_inventor_dwarf_helmet",
	]

	hero_items = inventory_items + hero_equipped + companion1_equipped + companion2_equipped

	print("=== Searching for Hero Inventory Items ===\n")

	results = search_for_items(data, hero_items)

	all_positions = []
	for item_name, positions in results.items():
		print(f"{item_name:45s}: {len(positions):3d} occurrences at {positions[:3]}")
		all_positions.extend(positions)

	print(f"\n{'='*80}")
	print("CLUSTER ANALYSIS")
	print(f"{'='*80}")

	analyze_item_cluster(data, all_positions)

	# Analyze first few items in detail
	print(f"\n{'='*80}")
	print("DETAILED ANALYSIS OF FIRST 3 ITEMS")
	print(f"{'='*80}")

	for item_name in hero_items[:3]:
		if item_name in results and results[item_name]:
			pos = results[item_name][0]
			print(f"\n{item_name} at position {pos}:")
			find_section_before_position(data, pos, distance=10000)
