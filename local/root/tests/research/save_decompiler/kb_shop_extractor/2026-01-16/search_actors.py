#!/usr/bin/env python3
from pathlib import Path
import struct

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# The inventory is at position 113231
# From the structure analysis, we know .actors is at position 111477
inventory_pos = 113231
actors_pos = 111477

print(f"Examining .actors section at position {actors_pos}")
print(f"Distance to inventory: {inventory_pos - actors_pos} bytes\n")

# Show context around the .actors section
context_start = actors_pos - 100
context_end = actors_pos + 200
context = data[context_start:context_end]

print("Context around .actors section:")
for i in range(0, len(context), 16):
	hex_line = " ".join(f"{b:02x}" for b in context[i:i+16])
	ascii_line = "".join(chr(b) if 32 <= b < 127 else "." for b in context[i:i+16])
	ctx_pos = context_start + i
	marker = " <-- .actors" if ctx_pos == actors_pos else ""
	print(f"{ctx_pos:08x}:  {hex_line:<48}  {ascii_line}{marker}")

# Try to extract actor ID from the .actors section
print("\n" + "="*80)
print("\nSearching for 'strg' field in .actors section:")

# Look for "strg" in the next 100 bytes after .actors
actors_chunk = data[actors_pos:actors_pos+100]
strg_pos = actors_chunk.find(b"strg")

if strg_pos != -1:
	abs_strg_pos = actors_pos + strg_pos
	print(f"Found 'strg' at position {abs_strg_pos} (0x{abs_strg_pos:x})")
	
	# The actor ID should be 4 bytes after "strg"
	# Check if the last byte has bit 7 set
	actor_bytes_pos = abs_strg_pos + 4  # Skip "strg" (4 bytes)
	if actor_bytes_pos + 4 <= len(data):
		actor_bytes = data[actor_bytes_pos:actor_bytes_pos+4]
		actor_value = struct.unpack("<I", actor_bytes)[0]
		
		# Check bit 7 of the last byte
		last_byte = actor_bytes[3]
		bit7_set = (last_byte & 0x80) != 0
		
		print(f"Actor bytes: {actor_bytes.hex()}")
		print(f"Actor value (raw): {actor_value}")
		print(f"Last byte: 0x{last_byte:02x}")
		print(f"Bit 7 set: {bit7_set}")
		
		if bit7_set:
			# Clear bit 7 to get actual actor ID
			clean_last_byte = last_byte & 0x7F
			clean_bytes = actor_bytes[:3] + bytes([clean_last_byte])
			clean_actor_id = struct.unpack("<I", clean_bytes)[0]
			print(f"Clean actor ID: {clean_actor_id}")
		else:
			print("This shop is inactive (bit 7 not set)")
else:
	print("'strg' not found in .actors section")
