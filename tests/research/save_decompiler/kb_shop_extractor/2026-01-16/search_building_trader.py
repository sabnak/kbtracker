#!/usr/bin/env python3
from pathlib import Path

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# Search for all building_trader@ near m_inselburg
location_bytes = b"m_inselburg"
results = []

pos = 0
while True:
	pos = data.find(location_bytes, pos)
	if pos == -1:
		break
	
	# Search for building_trader@ within 1000 bytes after location
	search_start = pos
	search_end = min(len(data), pos + 1000)
	chunk = data[search_start:search_end]
	
	trader_pos = chunk.find(b"building_trader@")
	if trader_pos != -1:
		abs_pos = search_start + trader_pos
		num_start = abs_pos + len(b"building_trader@")
		num_end = num_start
		while num_end < len(data) and data[num_end:num_end+1].isdigit():
			num_end += 1
		trader_num = data[num_start:num_end].decode("latin-1")
		
		# Get context
		context_start = max(0, abs_pos - 200)
		context_end = min(len(data), abs_pos + 300)
		context = data[context_start:context_end]
		
		results.append({
			"location_pos": pos,
			"trader_pos": abs_pos,
			"trader_num": trader_num,
			"context": context
		})
	
	pos += 1

print(f"Found {len(results)} building_trader@ occurrences near m_inselburg")
for i, r in enumerate(results):
	print(f"\n=== Occurrence {i+1} ===")
	print(f"Location position: {r['location_pos']} (0x{r['location_pos']:x})")
	print(f"Trader position: {r['trader_pos']} (0x{r['trader_pos']:x})")
	print(f"Trader number: {r['trader_num']}")
	print(f"\nContext (ASCII):")
	ascii_repr = r['context'].decode("latin-1", errors="replace")
	print(ascii_repr[:300])
