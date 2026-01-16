#!/usr/bin/env python3
from pathlib import Path

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# The inventory is at position 113231
# Let's search backwards from this position for any shop markers
inventory_pos = 113231

search_start = max(0, inventory_pos - 3000)
search_end = inventory_pos

print(f"Searching for shop markers before inventory position {inventory_pos}")
print(f"Search range: {search_start} to {search_end}\n")

# Search for building_trader@ in the range
chunk = data[search_start:search_end]
trader_pos = chunk.rfind(b"building_trader@")

if trader_pos != -1:
	abs_pos = search_start + trader_pos
	print(f"FOUND building_trader@ at position {abs_pos} (0x{abs_pos:x})")
	
	# Extract the number
	num_start = abs_pos + len(b"building_trader@")
	num_end = num_start
	while num_end < len(data) and data[num_end:num_end+1].isdigit():
		num_end += 1
	trader_num = data[num_start:num_end].decode("latin-1")
	print(f"Trader number: {trader_num}")
	
	# Show context
	context_start = abs_pos - 200
	context_end = abs_pos + 300
	context = data[context_start:context_end]
	
	print(f"\nContext around building_trader@{trader_num}:")
	for i in range(0, len(context), 16):
		hex_line = " ".join(f"{b:02x}" for b in context[i:i+16])
		ascii_line = "".join(chr(b) if 32 <= b < 127 else "." for b in context[i:i+16])
		ctx_pos = context_start + i
		marker = " <--" if ctx_pos == abs_pos else ""
		print(f"{ctx_pos:08x}:  {hex_line:<48}  {ascii_line}{marker}")
else:
	print("building_trader@ NOT FOUND in the range")

# Also search for m_inselburg
print("\n" + "="*80)
print("\nSearching for m_inselburg (ASCII) before inventory:")
inselburg_positions = []
pos = search_start
while pos < search_end:
	pos = data.find(b"m_inselburg", pos, search_end)
	if pos == -1:
		break
	inselburg_positions.append(pos)
	pos += 1

print(f"Found {len(inselburg_positions)} occurrences of m_inselburg:")
for pos in inselburg_positions:
	# Show a small context
	context = data[pos-20:pos+50].decode("latin-1", errors="replace")
	print(f"  Position {pos} (0x{pos:x}): ...{context}...")
