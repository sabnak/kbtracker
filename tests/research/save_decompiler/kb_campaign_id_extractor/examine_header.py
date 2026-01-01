"""
Examine the header area of info files in detail.
Focus on the first 512 bytes to find campaign ID.
"""
from pathlib import Path
import struct


def read_binary(file_path: Path, max_bytes: int = 512) -> bytes:
	"""Read first N bytes of file."""
	with open(file_path, 'rb') as f:
		return f.read(max_bytes)


def parse_field(data: bytes, offset: int) -> tuple[int, str, bytes]:
	"""
	Parse a field in the info file format.
	Returns: (next_offset, field_name, field_data)
	"""
	if offset + 8 > len(data):
		return offset, "EOF", b''

	# Read field size and type
	field_size = struct.unpack('<I', data[offset:offset+4])[0]
	field_type = struct.unpack('<I', data[offset+4:offset+8])[0]

	offset += 8

	# Read field data
	if offset + field_size > len(data):
		return offset, f"TRUNCATED_type_{field_type:02x}", b''

	field_data = data[offset:offset+field_size]
	offset += field_size

	# Try to decode as string
	try:
		field_name = field_data.decode('utf-16-le').rstrip('\x00')
	except:
		field_name = f"type_{field_type:02x}"

	return offset, field_name, field_data


def hex_dump(data: bytes, start_offset: int = 0, max_lines: int = 32) -> None:
	"""Pretty print hex dump."""
	for i in range(0, min(len(data), max_lines * 16), 16):
		hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
		print(f'  {start_offset + i:04x}  {hex_part:<48}  {ascii_part}')


def main():
	"""Analyze header area."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	saves = {
		'C1S1': saves_dir / '1707078232' / 'info',
		'C1S2': saves_dir / '1707047253' / 'info',
		'C2S1': saves_dir / '1766864874' / 'info',
		'C2S2': saves_dir / '1767209722' / 'info',
	}

	print("=" * 80)
	print("INFO FILE HEADER ANALYSIS")
	print("=" * 80)

	for name, path in saves.items():
		data = read_binary(path)
		print(f"\n{'=' * 80}")
		print(f"{name}: {path.parent.name}")
		print(f"{'=' * 80}")

		print("\nFirst 512 bytes hex dump:")
		hex_dump(data)

		# Parse fields
		print("\nParsed fields:")
		offset = 0

		# Header
		version = struct.unpack('<I', data[0:4])[0]
		header_size = struct.unpack('<I', data[4:8])[0]
		print(f"  Version/Type: 0x{version:08x}")
		print(f"  Header Size: {header_size}")

		offset = 8

		# Magic string
		magic = data[offset:offset+header_size].decode('utf-8', errors='ignore')
		print(f"  Magic: '{magic}'")
		offset += header_size

		# Parse next 10 fields
		for field_num in range(10):
			if offset >= len(data):
				break

			next_offset, field_name, field_data = parse_field(data, offset)

			print(f"\n  Field {field_num + 1} at offset 0x{offset:04x}:")
			print(f"    Name: {field_name}")
			print(f"    Size: {len(field_data)} bytes")

			# Show data interpretation
			if len(field_data) <= 32:
				print(f"    Hex: {field_data.hex()}")

				# Try various interpretations
				if len(field_data) == 4:
					val = struct.unpack('<I', field_data)[0]
					print(f"    As uint32: {val} (0x{val:08x})")
				elif len(field_data) == 8:
					val = struct.unpack('<Q', field_data)[0]
					print(f"    As uint64: {val} (0x{val:016x})")

				# Try string decode
				try:
					s = field_data.decode('utf-16-le').rstrip('\x00')
					if s and all(c.isprintable() or c in '\n\r\t' for c in s):
						print(f"    As UTF-16: '{s}'")
				except:
					pass

			offset = next_offset

	# Now specifically check offsets 0x010d and 0x010e
	print("\n" + "=" * 80)
	print("SPECIFIC OFFSET ANALYSIS: 0x010d - 0x0120")
	print("=" * 80)

	for name, path in saves.items():
		with open(path, 'rb') as f:
			f.seek(0x010d)
			chunk = f.read(20)

		print(f"\n{name}:")
		print(f"  Offset 0x010d-0x0120: {chunk.hex()}")

		# Try to decode as UTF-16
		try:
			s = chunk.decode('utf-16-le').rstrip('\x00')
			print(f"  As UTF-16: '{s}'")
		except:
			pass

		# Show as integers
		if len(chunk) >= 4:
			val = struct.unpack('<I', chunk[0:4])[0]
			print(f"  First 4 bytes as uint32: 0x{val:08x}")

		if len(chunk) >= 8:
			val = struct.unpack('<Q', chunk[0:8])[0]
			print(f"  First 8 bytes as uint64: 0x{val:016x}")


if __name__ == '__main__':
	main()
