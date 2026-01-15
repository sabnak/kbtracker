#!/usr/bin/env python3
"""Re-examine lookup table structure to find the bug in parsing"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('RE-EXAMINING LOOKUP TABLE STRUCTURE')
print('=' * 80)
print()

lookup_start = 2160000
lookup_end = 2180000
chunk = data[lookup_start:lookup_end]
text = chunk.decode('ascii', errors='ignore')

# Show raw text around building_trader@818 (which has actor_807991996)
print('1. Raw text around building_trader@818:')
print('-' * 80)

pos_818 = text.find('building_trader@818')
if pos_818 != -1:
	context = text[pos_818:pos_818+200]
	print(context)
	print()

print('=' * 80)
print()

# Search for "31" in the lookup table area
print('2. Searching for "31" in lookup table:')
print('-' * 80)

# Find all occurrences of "31" in lookup table
pattern = r'\b31\b'
matches = list(re.finditer(pattern, text))

print(f'Found {len(matches)} occurrences of "31" as separate token')
print()

for i, match in enumerate(matches[:10], 1):
	pos = match.start()
	context_start = max(0, pos - 100)
	context_end = min(len(text), pos + 100)
	context = text[context_start:context_end]

	print(f'{i}. Position {lookup_start + pos}:')
	print(f'   Context: {context}')
	print()

print('=' * 80)
print()

# Show the FULL structure of a few lookup table entries
print('3. Detailed structure of lookup table entries:')
print('-' * 80)

# Extract all building_trader@ entries with FULL context
pattern = r'building_trader@(\d+)([^b]*?)(?=building_trader@|\Z)'
matches = list(re.finditer(pattern, text))

print(f'Found {len(matches)} building_trader@ entries in lookup table')
print()

print('First 10 entries with FULL data between them:')
for i, match in enumerate(matches[:10], 1):
	building_num = match.group(1)
	full_data = match.group(2)

	print(f'{i}. building_trader@{building_num}')
	print(f'   Following data: {full_data[:200]}')

	# Try to extract actor ID
	actor_match = re.search(r'\b(\d{8,9})\b', full_data)
	if actor_match:
		actor_id = actor_match.group(1)
		print(f'   → Extracted actor ID: {actor_id}')

	print()

print('=' * 80)
print()

# Check if there's a pattern of "lu" (list unit?) markers
print('4. Checking for "lu" markers (might indicate list structure):')
print('-' * 80)

lu_pattern = r'\blu\b'
lu_matches = list(re.finditer(lu_pattern, text))
print(f'Found {len(lu_matches)} "lu" markers in lookup table')
print()

# Show pattern around lu markers
for match in lu_matches[:15]:
	pos = match.start()
	context = text[max(0, pos-30):min(len(text), pos+30)]
	print(f'Position {lookup_start + pos}: ...{context}...')

print()
print('=' * 80)
