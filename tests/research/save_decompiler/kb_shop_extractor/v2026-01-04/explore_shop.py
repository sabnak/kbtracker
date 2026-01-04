"""
Interactive Shop Explorer using Construct

This script uses Construct library to explore shop data from King's Bounty save files.
It helps investigate parsing issues by visualizing the binary structure.

Usage:
	python explore_shop.py <shop_id>

Examples:
	python explore_shop.py m_atrixus_late_708
	python explore_shop.py m_atrixus_10

Author: Claude (Anthropic)
Date: 2026-01-04
"""

import sys
import struct
from pathlib import Path as FilePath
from construct import *

# Add parent directories to path for imports
sys.path.insert(0, str(FilePath(__file__).parent.parent.parent.parent.parent.parent))

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


# =============================================================================
# Configuration
# =============================================================================

SAVE_FILE_PATH = "/app/tests/game_files/saves/1707047253/data"


# =============================================================================
# Helper Functions
# =============================================================================

def find_shop_in_data(data: bytes, shop_id: str) -> int:
	"""
	Find shop ID position in decompressed data

	:param data:
		Decompressed save file data
	:param shop_id:
		Shop ID without "itext_" prefix (e.g., "m_atrixus_10")
	:return:
		Position of shop ID, or -1 if not found
	"""
	# Try with "itext_" prefix
	full_id = f"itext_{shop_id}"
	shop_bytes = full_id.encode('utf-16-le')
	pos = data.find(shop_bytes)

	if pos != -1:
		print(f"✓ Found shop '{full_id}' at position {pos}")
		return pos

	# Try without prefix
	shop_bytes = shop_id.encode('utf-16-le')
	pos = data.find(shop_bytes)

	if pos != -1:
		print(f"✓ Found shop '{shop_id}' at position {pos}")
		return pos

	return -1


def find_section(data: bytes, shop_pos: int, marker: bytes, max_distance: int = 5000) -> int:
	"""
	Find section marker before shop ID

	:param data:
		Save file data
	:param shop_pos:
		Shop ID position
	:param marker:
		Section marker
	:param max_distance:
		Max search distance
	:return:
		Section position or -1
	"""
	search_start = max(0, shop_pos - max_distance)
	chunk = data[search_start:shop_pos]
	last_pos = chunk.rfind(marker)

	if last_pos != -1:
		actual_pos = search_start + last_pos
		distance = shop_pos - actual_pos
		print(f"  ✓ Found {marker.decode('ascii', errors='ignore')} at {actual_pos} (distance: {distance} bytes)")
		return actual_pos

	return -1


def hex_dump(data: bytes, offset: int = 0, length: int = 256, highlight_positions: list[int] = None) -> None:
	"""
	Print hex dump of data with optional highlights

	:param data:
		Binary data
	:param offset:
		Starting offset
	:param length:
		Number of bytes to display
	:param highlight_positions:
		List of positions to highlight
	"""
	highlight_positions = highlight_positions or []
	end = min(offset + length, len(data))

	print("\nHex Dump:")
	print("Offset    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  ASCII")
	print("-" * 70)

	for i in range(offset, end, 16):
		# Offset
		print(f"{i:08X}  ", end="")

		# Hex bytes
		for j in range(16):
			if i + j < end:
				byte = data[i + j]
				if i + j in highlight_positions:
					print(f"\033[91m{byte:02X}\033[0m ", end="")  # Red highlight
				else:
					print(f"{byte:02X} ", end="")
				if j == 7:
					print(" ", end="")
			else:
				print("   ", end="")
				if j == 7:
					print(" ", end="")

		print(" ", end="")

		# ASCII representation
		for j in range(16):
			if i + j < end:
				byte = data[i + j]
				char = chr(byte) if 32 <= byte < 127 else '.'
				print(char, end="")

		print()


def explore_section(data: bytes, section_name: str, section_pos: int, next_pos: int) -> None:
	"""
	Explore a section using Construct

	:param data:
		Save file data
	:param section_name:
		Section name for display
	:param section_pos:
		Section start position
	:param next_pos:
		Position of next section or shop ID
	"""
	if section_pos == -1:
		print(f"\n❌ Section {section_name} not found")
		return

	section_size = next_pos - section_pos
	section_data = data[section_pos:next_pos]

	print(f"\n{'=' * 70}")
	print(f"Section: {section_name}")
	print(f"Position: {section_pos}")
	print(f"Size: {section_size} bytes")
	print(f"Next boundary: {next_pos}")
	print(f"{'=' * 70}")

	# Hex dump first 256 bytes
	hex_dump(section_data, 0, min(256, len(section_data)))

	# Try to parse based on section type
	print(f"\n--- Attempting to parse {section_name} ---")

	if section_name in [".shopunits", ".garrison"]:
		# Slash-separated format
		parse_slash_separated_section(section_data)
	elif section_name == ".items":
		parse_items_section(section_data)
	elif section_name == ".spells":
		parse_spells_section(section_data)


def parse_slash_separated_section(data: bytes) -> None:
	"""Parse slash-separated section (units/garrison)"""
	try:
		# Find "strg" marker
		strg_pos = data.find(b'strg')
		if strg_pos == -1:
			print("  ❌ No 'strg' marker found")
			return

		print(f"  ✓ Found 'strg' marker at offset {strg_pos}")

		# Read string length (4 bytes after 'strg')
		pos = strg_pos + 4
		if pos + 4 > len(data):
			print("  ❌ Not enough data for length field")
			return

		str_length = struct.unpack('<I', data[pos:pos+4])[0]
		print(f"  ✓ String length: {str_length}")

		# Read string content
		pos += 4
		if pos + str_length > len(data):
			print(f"  ❌ Not enough data for content (need {str_length} bytes)")
			return

		content = data[pos:pos+str_length].decode('ascii')
		print(f"  ✓ Content: {content}")

		# Parse slash-separated format
		parts = content.split('/')
		print(f"  ✓ Parsed {len(parts) // 2} entries:")

		i = 0
		while i < len(parts) - 1:
			name = parts[i]
			try:
				quantity = int(parts[i + 1])
				print(f"    - {name}: {quantity}")
				i += 2
			except (ValueError, IndexError):
				print(f"    ⚠ Skipped invalid entry: {parts[i]}")
				i += 1

	except Exception as e:
		print(f"  ❌ Error parsing: {e}")


def parse_items_section(data: bytes) -> None:
	"""Parse items section with length-prefixed entries"""
	try:
		pos = len(b'.items')  # Skip marker
		items_found = []

		print("  Scanning for length-prefixed strings...")

		while pos < len(data) - 8:
			# Try to read length
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			# Validate length
			if 5 <= name_length <= 100:
				if pos + 4 + name_length > len(data):
					pos += 1
					continue

				try:
					name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					# Validate name pattern
					if name.replace('_', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '').isalpha():
						items_found.append((pos, name))
						print(f"    {len(items_found)}. At offset {pos}: '{name}' (length={name_length})")
						pos += 4 + name_length
						continue
				except UnicodeDecodeError:
					pass

			pos += 1

		print(f"  ✓ Found {len(items_found)} potential items")

	except Exception as e:
		print(f"  ❌ Error parsing: {e}")


def parse_spells_section(data: bytes) -> None:
	"""Parse spells section with length-prefixed entries + quantity"""
	try:
		pos = len(b'.spells')  # Skip marker
		spells_found = []

		print("  Scanning for length-prefixed strings + quantity...")

		while pos < len(data) - 12:
			# Try to read length
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			# Validate length
			if 5 <= name_length <= 100:
				if pos + 4 + name_length + 4 > len(data):
					pos += 1
					continue

				try:
					name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					# Validate name pattern
					if name.replace('_', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '').isalpha():
						# Try to read quantity
						quantity = struct.unpack('<I', data[pos+4+name_length:pos+4+name_length+4])[0]

						if 0 < quantity < 10000:
							spells_found.append((pos, name, quantity))
							print(f"    {len(spells_found)}. At offset {pos}: '{name}' x{quantity} (length={name_length})")
							pos += 4 + name_length + 4
							continue
				except UnicodeDecodeError:
					pass

			pos += 1

		print(f"  ✓ Found {len(spells_found)} potential spells")

	except Exception as e:
		print(f"  ❌ Error parsing: {e}")


# =============================================================================
# Main Script
# =============================================================================

def main():
	"""Main exploration script"""
	if len(sys.argv) < 2:
		print("Usage: python explore_shop.py <shop_id>")
		print("Example: python explore_shop.py m_atrixus_late_708")
		sys.exit(1)

	shop_id = sys.argv[1]

	print(f"\n{'=' * 70}")
	print(f"King's Bounty Shop Explorer - Construct Library")
	print(f"{'=' * 70}")
	print(f"Shop ID: {shop_id}")
	print(f"Save File: {SAVE_FILE_PATH}")

	# Decompress save file
	print("\n1. Decompressing save file...")
	decompressor = SaveFileDecompressor()
	save_path = FilePath(SAVE_FILE_PATH)
	data = decompressor.decompress(save_path)
	print(f"✓ Decompressed {len(data):,} bytes")

	# Find shop
	print(f"\n2. Finding shop '{shop_id}'...")
	shop_pos = find_shop_in_data(data, shop_id)

	if shop_pos == -1:
		print(f"❌ Shop '{shop_id}' not found in save file")
		sys.exit(1)

	# Find sections
	print("\n3. Finding sections...")
	garrison_pos = find_section(data, shop_pos, b'.garrison')
	items_pos = find_section(data, shop_pos, b'.items')
	units_pos = find_section(data, shop_pos, b'.shopunits')
	spells_pos = find_section(data, shop_pos, b'.spells')

	# Determine section order and boundaries
	sections = []
	if garrison_pos != -1:
		sections.append(('.garrison', garrison_pos))
	if items_pos != -1:
		sections.append(('.items', items_pos))
	if units_pos != -1:
		sections.append(('.shopunits', units_pos))
	if spells_pos != -1:
		sections.append(('.spells', spells_pos))

	sections.sort(key=lambda x: x[1])

	# Explore each section
	print("\n4. Exploring sections...")
	for i, (section_name, section_pos) in enumerate(sections):
		# Determine next boundary
		if i + 1 < len(sections):
			next_pos = sections[i + 1][1]
		else:
			next_pos = shop_pos

		explore_section(data, section_name, section_pos, next_pos)

	print(f"\n{'=' * 70}")
	print("Exploration complete!")
	print(f"{'=' * 70}\n")


if __name__ == "__main__":
	main()

