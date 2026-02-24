#!/usr/bin/env python3
from pathlib import Path

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# The .temp section is at position 113497
# Let's search forward from there
temp_pos = 113497

print(f"Searching forward from .temp section at position {temp_pos}\n")

# Search for building_trader@ in the next 1000 bytes
search_start = temp_pos
search_end = min(len(data), temp_pos + 1000)
chunk = data[search_start:search_end]

trader_pos = chunk.find(b"building_trader@")
if trader_pos != -1:
	abs_pos = search_start + trader_pos
	print(f"FOUND building_trader@ at position {abs_pos} (0x{abs_pos:x})")
	
	# Extract number
	num_start = abs_pos + len(b"building_trader@")
	num_end = num_start
	while num_end < len(data) and data[num_end:num_end+1].isdigit():
		num_end += 1
	trader_num = data[num_start:num_end].decode("latin-1")
	print(f"Trader number: {trader_num}")
	
	# Show context
	context_start = abs_pos - 300
	context_end = abs_pos + 300
	context = data[context_start:context_end]
	
	print(f"\nContext around building_trader@{trader_num}:")
	for i in range(0, len(context), 16):
		hex_line = " ".join(f"{b:02x}" for b in context[i:i+16])
		ascii_line = "".join(chr(b) if 32 <= b < 127 else "." for b in context[i:i+16])
		ctx_pos = context_start + i
		marker = " <-- building_trader@" if ctx_pos == abs_pos else ""
		print(f"{ctx_pos:08x}:  {hex_line:<48}  {ascii_line}{marker}")
else:
	print("building_trader@ NOT FOUND in the next 1000 bytes")
	
# Also search for "lt" (location tag) and m_inselburg
print("\n" + "="*80)
lt_pos = chunk.find(b"lt")
if lt_pos != -1:
	abs_lt = search_start + lt_pos
	print(f"\nFound 'lt' tag at position {abs_lt} (0x{abs_lt:x})")
	
	# Show what comes after lt
	lt_context = data[abs_lt:abs_lt+50]
	print(f"After 'lt': {lt_context}")
