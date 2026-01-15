#!/usr/bin/env python3
"""Try to understand what the lookup table actually represents"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('UNDERSTANDING LOOKUP TABLE STRUCTURE')
print('=' * 80)
print()

# Get all actual building_trader@ numbers in the save
actual_traders = []
for match in re.finditer(rb'building_trader@(\d+)(?!\d)', data):
	pos = match.start()
	num = int(match.group(1).decode('ascii'))
	# Skip if in lookup table area
	if not (2160000 <= pos <= 2180000):
		# Check if has inventory
		has_inventory = b'.shopunits' in data[max(0, pos - 1000):pos]
		actual_traders.append((num, pos, has_inventory))

actual_traders.sort(key=lambda x: x[0])

print(f'Found {len(actual_traders)} actual building_trader@ in save data')
print()

# Get all building_trader@ references in lookup table
lookup_start = 2160000
lookup_end = 2180000
chunk = data[lookup_start:lookup_end]
text = chunk.decode('ascii', errors='ignore')

pattern = r'building_trader@(\d+).{1,50}se\D+(\d+)'
lookup_matches = list(re.finditer(pattern, text))

lookup_entries = []
for match in lookup_matches:
	table_num = int(match.group(1))
	actor_id = int(match.group(2))
	lookup_entries.append((table_num, actor_id))

lookup_entries.sort(key=lambda x: x[0])

print(f'Found {len(lookup_entries)} entries in lookup table')
print()

# Compare the two lists
print('Comparison:')
print('-' * 80)
print()

print('Building_trader@ numbers in ACTUAL save data:')
actual_nums = set(x[0] for x in actual_traders if x[2])  # Only with inventory
print(f'{sorted(actual_nums)[:20]}... (first 20)')
print()

print('Building_trader@ numbers in LOOKUP TABLE:')
lookup_nums = set(x[0] for x in lookup_entries)
print(f'{sorted(lookup_nums)[:20]}... (first 20)')
print()

# Check overlap
overlap = actual_nums & lookup_nums
print(f'Numbers in BOTH actual save and lookup table: {len(overlap)}')
if overlap:
	print(f'  Examples: {sorted(overlap)[:10]}')
print()

only_actual = actual_nums - lookup_nums
print(f'Numbers ONLY in actual save (not in lookup): {len(only_actual)}')
if only_actual:
	print(f'  Examples: {sorted(only_actual)[:10]}')
print()

only_lookup = lookup_nums - actual_nums
print(f'Numbers ONLY in lookup table (not in save): {len(only_lookup)}')
if only_lookup:
	print(f'  Examples: {sorted(only_lookup)[:10]}')
print()

print('=' * 80)
print()

# Check if the lookup table might be from a different game state / old data
print('HYPOTHESIS: Lookup table is from old/different game state')
print('-' * 80)
print()

# Check if any of the lookup table building_trader@ numbers exist as entries without inventory
print('Do lookup table numbers exist as non-shop entries?')
for lookup_num in sorted(only_lookup)[:10]:
	# Find this number in actual save
	exists = any(x[0] == lookup_num for x in actual_traders)
	if exists:
		has_inv = any(x[0] == lookup_num and x[2] for x in actual_traders)
		print(f'  building_trader@{lookup_num}: exists={exists}, has_inventory={has_inv}')

print()
print('=' * 80)
print()

# Different approach: maybe the lookup is indexed, not by building_trader number
print('ALTERNATIVE: Maybe lookup table is ORDERED, not keyed by building_trader@')
print('-' * 80)
print()

print('If we match by position in the lists:')
print('  Actual traders (sorted): ', [x[0] for x in actual_traders if x[2]][:10])
print('  Lookup entries (sorted): ', [x[0] for x in lookup_entries][:10])
print()

# Show side-by-side comparison
print('Position-based matching (first 15):')
print(f'{"Index":<6} {"Actual":>15} {"Lookup":>15} {"Actor ID":>12}')
print('-' * 60)

actual_with_inv = [x for x in actual_traders if x[2]]
for i in range(min(15, len(actual_with_inv), len(lookup_entries))):
	actual_num = actual_with_inv[i][0]
	lookup_num, actor_id = lookup_entries[i]
	match = "✓" if actual_num == lookup_num else "✗"
	print(f'{i:<6} trader@{actual_num:>6} trader@{lookup_num:>6}  {actor_id:>12}  {match}')

print()
print('=' * 80)
