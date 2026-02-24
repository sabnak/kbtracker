#!/usr/bin/env python3
from pathlib import Path

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# The inventory starts at position 113231
inventory_pos = 113231

# Search backwards for shop structure markers
search_start = max(0, inventory_pos - 2000)
search_end = min(len(data), inventory_pos + 2000)
chunk = data[search_start:search_end]

print("=== Shop Structure Analysis ===")
print(f"Inventory position: {inventory_pos} (0x{inventory_pos:x})")
print(f"Analyzing range: {search_start} to {search_end}\n")

# Find key markers in the chunk
markers = {
	b".shopunits": [],
	b".items": [],
	b".spells": [],
	b".garrison": [],
	b".temp": [],
	b".actors": [],
	b"building_trader@": [],
	b"m_inselburg": [],
	b"itext_": []
}

for marker, positions in markers.items():
	pos = 0
	while True:
		pos = chunk.find(marker, pos)
		if pos == -1:
			break
		abs_pos = search_start + pos
		positions.append(abs_pos)
		pos += 1

print("Markers found:")
for marker, positions in sorted(markers.items(), key=lambda x: x[1][0] if x[1] else 999999):
	if positions:
		print(f"  {marker.decode('latin-1', errors='replace'):20s}: {positions}")

# Show hex dump around the inventory position
print(f"\n=== Hex dump around inventory (position {inventory_pos}) ===\n")
dump_start = inventory_pos - 300
dump_end = inventory_pos + 700
dump_chunk = data[dump_start:dump_end]

for i in range(0, len(dump_chunk), 16):
	hex_line = " ".join(f"{b:02x}" for b in dump_chunk[i:i+16])
	ascii_line = "".join(chr(b) if 32 <= b < 127 else "." for b in dump_chunk[i:i+16])
	abs_pos = dump_start + i
	marker = " <-- INVENTORY" if abs_pos == inventory_pos else ""
	print(f"{abs_pos:08x}:  {hex_line:<48}  {ascii_line}{marker}")
