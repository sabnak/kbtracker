#!/usr/bin/env python3
"""Test trader ID map extraction"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('Testing trader ID map extraction:')
print('=' * 80)
print()

# Test the pattern on known good examples
lookup_start = 2160000
lookup_end = 2180000

chunk = data[lookup_start:lookup_end]

try:
	text = chunk.decode('ascii', errors='ignore')

	# Show sample of the lookup table
	print('Sample of lookup table text:')
	print(text[8000:8500])
	print()

	# Try the pattern (CORRECTED)
	pattern = r'building_trader@(\d+)\s+se\s+(\d{8,})'
	matches = list(re.finditer(pattern, text))

	print(f'Pattern matches: {len(matches)}')
	print()

	if matches:
		print('First 10 matches:')
		for match in matches[:10]:
			building_num = match.group(1)
			trader_id = match.group(2)
			print(f'  building_trader@{building_num} -> actor_{trader_id}')
	else:
		print('No matches found!')
		print()
		print('Trying simpler pattern:')

		# Try simpler pattern
		simple_pattern = r'building_trader@(\d+).*?se\s+(\d{8,})'
		simple_matches = list(re.finditer(simple_pattern, text))

		print(f'Simple pattern matches: {len(simple_matches)}')

		if simple_matches:
			for match in simple_matches[:10]:
				building_num = match.group(1)
				trader_id = match.group(2)
				print(f'  building_trader@{building_num} -> actor_{trader_id}')

	print()

	# Check for building_trader@818 specifically
	print('Looking for building_trader@818 (should map to 807991996):')
	idx = text.find('building_trader@818')
	if idx != -1:
		context = text[idx:idx+200]
		print(f'  Context: {context}')

except Exception as e:
	print(f'Error: {e}')
