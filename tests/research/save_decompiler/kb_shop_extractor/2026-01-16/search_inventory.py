#!/usr/bin/env python3
from pathlib import Path

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# Search for the specific units mentioned in the expected inventory
units = ["pirat2", "robber", "assassin", "spider_venom", "spider_fire"]
items = ["addon2_belt_obeliks_belt", "astral_bow"]
spells = ["fire_arrow", "advspell_summon_bandit", "titan_sword"]

print("Searching for expected inventory items...")

for unit in units:
	positions = []
	search_bytes = unit.encode("latin-1")
	pos = 0
	while True:
		pos = data.find(search_bytes, pos)
		if pos == -1:
			break
		positions.append(pos)
		pos += 1
	print(f"\n{unit}: {len(positions)} occurrences")
	if positions:
		print(f"  First 5 positions: {positions[:5]}")

# Look for the specific quantity pattern pirat2/2580
print("\n\nSearching for specific quantity patterns:")
patterns = [
	b"pirat2/2580",
	b"robber/2140",
	b"assassin/300",
	b"spider_venom/9000",
	b"spider_fire/9200"
]

for pattern in patterns:
	pos = data.find(pattern)
	if pos != -1:
		print(f"\nFOUND: {pattern.decode()} at position {pos} (0x{pos:x})")
		
		# Get context
		context_start = max(0, pos - 500)
		context_end = min(len(data), pos + 500)
		context = data[context_start:context_end]
		
		# Look for shop identifier backwards from this position
		# Search for itext_ or building_trader@ in the context
		itext_pos = context.rfind(b"itext_")
		trader_pos = context.rfind(b"building_trader@")
		
		if itext_pos != -1:
			# Extract the shop ID
			itext_start = context_start + itext_pos
			itext_chunk = data[itext_start:itext_start+100]
			# Try to decode as UTF-16 LE
			try:
				decoded = itext_chunk.decode("utf-16-le", errors="ignore")
				shop_id = decoded.split("\x00")[0]
				print(f"  Nearby itext identifier: {shop_id} at position {itext_start}")
			except:
				pass
		
		if trader_pos != -1:
			trader_start = context_start + trader_pos
			print(f"  Nearby building_trader@ at position {trader_start}")
	else:
		print(f"NOT FOUND: {pattern.decode()}")
