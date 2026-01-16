#!/usr/bin/env python3
from pathlib import Path

def get_context(data: bytes, position: int, before: int = 200, after: int = 500) -> str:
	start = max(0, position - before)
	end = min(len(data), position + after)
	chunk = data[start:end]
	
	result = []
	result.append(f"=== Position {position} (0x{position:x}) ===")
	result.append(f"Range: {start} to {end}\n")
	
	# Show hex dump
	for i in range(0, min(len(chunk), 400), 16):
		hex_line = " ".join(f"{b:02x}" for b in chunk[i:i+16])
		ascii_line = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk[i:i+16])
		abs_pos = start + i
		marker = " <--" if abs_pos == position else ""
		result.append(f"{abs_pos:08x}:  {hex_line:<48}  {ascii_line}{marker}")
	
	return "\n".join(result)

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

positions = [113773, 113875, 7757345, 7757447]

for pos in positions:
	print(get_context(data, pos))
	print("\n" + "="*80 + "\n")
