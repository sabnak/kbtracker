#!/usr/bin/env python3
"""
Deep dive into Section 4 to find why tournament_helm is missing
"""
import struct
import os


def hex_dump(data: bytes, start: int, length: int = 512, highlight_pos: int = None):
	"""Print hex dump with optional highlight"""
	for i in range(0, length, 16):
		offset = start + i
		if offset >= len(data):
			break

		chunk = data[offset:offset+16]
		hex_part = ' '.join(f'{b:02X}' for b in chunk).ljust(48)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)

		marker = '>>>' if highlight_pos and start + i <= highlight_pos < start + i + 16 else '   '
		print(f"{marker} {offset:08X}  {hex_part}  {ascii_part}")


def parse_section_detailed(data: bytes, section_pos: int):
	"""Parse section with detailed logging"""
	print(f"\n{'='*78}")
	print(f"Parsing .items section at offset {section_pos} (0x{section_pos:X})")
	print(f"{'='*78}")

	pos = section_pos + len(b'.items')

	# Skip to 'strg' marker
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos == -1:
		print("No 'strg' marker found!")
		return

	print(f"\n'strg' marker at offset: {strg_pos} (0x{strg_pos:X})")
	pos = strg_pos + 4

	# Read item count
	item_count = struct.unpack('<I', data[pos:pos+4])[0]
	print(f"Item count: {item_count}")
	pos += 4

	print(f"Metadata bytes: {data[pos:pos+8].hex()}")
	pos += 8

	print(f"\nStarting item parsing at offset {pos} (0x{pos:X})")

	# Parse each item with detailed logging
	for i in range(min(item_count, 20)):
		print(f"\n{'-'*78}")
		print(f"Item {i}:")

		if pos + 4 > len(data):
			print("  ERROR: Not enough data for length field")
			break

		# Read length
		item_length = struct.unpack('<I', data[pos:pos+4])[0]
		print(f"  Length field at {pos}: {item_length}")

		if item_length <= 0 or item_length > 200:
			print(f"  ERROR: Invalid length {item_length}")
			break

		pos += 4

		if pos + item_length > len(data):
			print(f"  ERROR: Not enough data for item (need {item_length} bytes)")
			break

		# Read item name
		try:
			item_name = data[pos:pos+item_length].decode('ascii', errors='strict')
			print(f"  Name: '{item_name}'")

			item_end = pos + item_length

			# Show the bytes around this item
			print(f"  Hex dump around item:")
			hex_dump(data, pos - 4, min(item_length + 64, 128))

			pos = item_end

			# Now look for next item
			print(f"\n  Searching for next item starting at {pos} (0x{pos:X})...")

			max_skip = 200
			found_next = False
			for skip in range(max_skip):
				if pos + skip + 4 > len(data):
					break

				next_len = struct.unpack('<I', data[pos+skip:pos+skip+4])[0]

				# Check if this looks like a valid item name length
				if 5 <= next_len <= 100:
					try:
						test_name = data[pos+skip+4:pos+skip+4+min(next_len, 50)].decode('ascii', errors='strict')
						if '_' in test_name and test_name[0].isalpha():
							print(f"  Found next item at offset +{skip}: '{test_name}'")
							pos += skip
							found_next = True
							break
					except:
						pass

			if not found_next:
				print(f"  No more items found (searched {max_skip} bytes from {item_end})")
				print(f"\n  Hex dump of search area:")
				hex_dump(data, item_end, 256)
				break

		except Exception as e:
			print(f"  ERROR decoding item: {e}")
			hex_dump(data, pos - 4, 64)
			break


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Section 4 is at offset 627891
	section4_pos = 627891

	parse_section_detailed(data, section4_pos)

	# Also check where tournament_helm is
	print(f"\n\n{'='*78}")
	print("Searching for tournament_helm...")
	print(f"{'='*78}")

	tournament_pos = data.find(b'tournament_helm')
	if tournament_pos != -1:
		print(f"\nFound at offset {tournament_pos} (0x{tournament_pos:X})")

		# Check if there's a length prefix
		if tournament_pos >= 4:
			possible_length = struct.unpack('<I', data[tournament_pos-4:tournament_pos])[0]
			print(f"Possible length prefix: {possible_length} (expected: {len('tournament_helm')})")

		print(f"\nHex dump around tournament_helm:")
		hex_dump(data, tournament_pos - 64, 192, tournament_pos)

		# Calculate distance from Section 4
		print(f"\nDistance from Section 4 start: {tournament_pos - section4_pos} bytes")
