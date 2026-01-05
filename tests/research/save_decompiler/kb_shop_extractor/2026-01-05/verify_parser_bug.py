#!/usr/bin/env python3
"""
Verify the parser bug by simulating _parse_slash_separated with invalid range
"""
import struct
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

decompressor = SaveFileDecompressor()
save_path = Path("/saves/Darkside/1767631838/data")
data = decompressor.decompress(save_path)

print("=" * 80)
print("SIMULATING PARSER BUG")
print("=" * 80)
print()

# Shop position
shop_pattern = "itext_m_portland_8671".encode("utf-16-le")
shop_pos = data.find(shop_pattern)

# Section positions
search_start = max(0, shop_pos - 5000)
chunk = data[search_start:shop_pos]

spells_pos = search_start + chunk.rfind(b".spells")
shopunits_pos = search_start + chunk.rfind(b".shopunits")
temp_pos = search_start + chunk.rfind(b".temp")

print(f"spells_pos    = {spells_pos}")
print(f"shopunits_pos = {shopunits_pos}")
print(f"temp_pos      = {temp_pos}")
print(f"shop_pos      = {shop_pos}")
print()

# Simulate parser logic (lines 397-400)
print("=" * 80)
print("SIMULATING ShopInventoryParser._parse_shop() lines 397-400")
print("=" * 80)
print()

units_pos = shopunits_pos

print("Code:")
print("  if units_pos:")
print("      next_pos = spells_pos if spells_pos else shop_pos")
print("      actual_end = self._find_section_end(data, units_pos, next_pos)")
print("      result[units] = self._parse_slash_separated(data, units_pos, actual_end)")
print()

next_pos = spells_pos if spells_pos else shop_pos
print(f"  next_pos = {next_pos} (spells_pos)")
print()

# Simulate _find_section_end
SECTION_MARKERS = {b".items", b".spells", b".shopunits", b".garrison", b".temp"}
search_area = data[units_pos:next_pos]

print(f"  _find_section_end(data, {units_pos}, {next_pos})")
print(f"  search_area = data[{units_pos}:{next_pos}]")
print(f"  search_area length = {len(search_area)} bytes")
print()

if len(search_area) <= 0:
    print("  ERROR: search_area is EMPTY or NEGATIVE!")
    print("  This is because next_pos < units_pos")
    print()
    print("  When search_area is empty:")
    print("    - search_area.find(marker, 1) will always return -1")
    print("    - earliest_marker_pos will remain = next_pos")
    print("    - actual_end = next_pos = {next_pos}")
    actual_end = next_pos
else:
    earliest_marker_pos = next_pos
    for marker in SECTION_MARKERS:
        pos = search_area.find(marker, 1)
        if pos != -1:
            absolute_pos = units_pos + pos
            earliest_marker_pos = min(earliest_marker_pos, absolute_pos)
    actual_end = earliest_marker_pos

print(f"  actual_end = {actual_end}")
print()

# Simulate _parse_slash_separated
print("=" * 80)
print("SIMULATING _parse_slash_separated")
print("=" * 80)
print()

print(f"  _parse_slash_separated(data, {units_pos}, {actual_end})")
print()

section_pos = units_pos
next_pos_param = actual_end

print(f"  section_pos = {section_pos}")
print(f"  next_pos = {next_pos_param}")
print()

if next_pos_param <= section_pos:
    print(f"  CRITICAL: next_pos ({next_pos_param}) <= section_pos ({section_pos})")
    print("  The parser will search for strg in an INVALID range!")
    print()

# Try to find strg
strg_pos_search = data.find(b"strg", section_pos, next_pos_param)
print(f"  data.find(b\"strg\", {section_pos}, {next_pos_param}) = {strg_pos_search}")
print()

if strg_pos_search == -1:
    print("  Result: strg marker NOT found (expected, since range is backwards)")
    print("  Parser returns: []")
else:
    print("  Result: strg found (unexpected)")

print()
print("=" * 80)
print("CORRECT APPROACH")
print("=" * 80)
print()

print("The parser should use the NEXT section marker AFTER .shopunits, not BEFORE")
print()
print("Correct logic:")
print("  if units_pos:")
print("      # Find next section AFTER units_pos")
print("      next_pos = shop_pos  # Default to shop ID")
print("      ")
print("      # Check if there are sections AFTER units_pos and BEFORE shop_pos")
print("      for marker in [spells_pos, temp_pos, items_pos, garrison_pos]:")
print("          if marker and units_pos < marker < shop_pos:")
print("              next_pos = min(next_pos, marker)")
print()

# Calculate correct range
correct_next_pos = shop_pos
if temp_pos and units_pos < temp_pos < shop_pos:
    correct_next_pos = min(correct_next_pos, temp_pos)
if spells_pos and units_pos < spells_pos < shop_pos:
    correct_next_pos = min(correct_next_pos, spells_pos)

print(f"  Correct next_pos = {correct_next_pos} (temp_pos)")
print()

# Parse with correct range
print("Parsing with CORRECT range:")
strg_pos_correct = data.find(b"strg", units_pos, correct_next_pos)
print(f"  data.find(b\"strg\", {units_pos}, {correct_next_pos}) = {strg_pos_correct}")

if strg_pos_correct != -1:
    str_len = struct.unpack("<I", data[strg_pos_correct + 4:strg_pos_correct + 8])[0]
    str_content = data[strg_pos_correct + 8:strg_pos_correct + 8 + str_len].decode("ascii")
    print(f"  String content: {str_content}")
    print()
    print("  UNITS FOUND:")
    parts = str_content.split("/")
    i = 0
    while i < len(parts) - 1:
        print(f"    - {parts[i]}: {parts[i+1]}")
        i += 2

