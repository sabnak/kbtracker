#!/usr/bin/env python3
import struct
import zlib
from pathlib import Path

def decompress_save(save_path: Path) -> bytes:
	data_file = save_path / "data"
	if not data_file.exists():
		raise FileNotFoundError(f"Data file not found: {data_file}")
	with open(data_file, "rb") as f:
		data = f.read()
	magic = data[0:4]
	if magic != b"slcb":
		raise ValueError(f"Invalid magic: {magic}")
	decompressed_size = struct.unpack("<I", data[4:8])[0]
	compressed_size = struct.unpack("<I", data[8:12])[0]
	compressed_data = data[12:12 + compressed_size]
	decompressed_data = zlib.decompress(compressed_data)
	if len(decompressed_data) != decompressed_size:
		raise ValueError(f"Size mismatch: {len(decompressed_data)} vs {decompressed_size}")
	return decompressed_data

def search_shop_identifier(data: bytes, shop_id: str) -> list:
	search_term = f"itext_{shop_id}".encode("utf-16-le")
	positions = []
	pos = 0
	while True:
		pos = data.find(search_term, pos)
		if pos == -1:
			break
		positions.append(pos)
		pos += 1
	return positions

save_path = Path("/app/tests/game_files/saves/quick1768586988")
print(f"Decompressing save file: {save_path}")
data = decompress_save(save_path)
print(f"Decompressed size: {len(data)} bytes")

output_dir = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16")
decompressed_file = output_dir / "decompressed_data.bin"
with open(decompressed_file, "wb") as f:
	f.write(data)
print(f"Saved decompressed data to: {decompressed_file}")

shop_id = "m_inselburg_6529"
print(f"\nSearching for: itext_{shop_id}")
positions = search_shop_identifier(data, shop_id)

if not positions:
	print(f"NOT FOUND: itext_{shop_id}")
else:
	print(f"FOUND at {len(positions)} position(s): {positions}")
