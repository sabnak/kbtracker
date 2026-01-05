#!/usr/bin/env python3
"""
Detailed analysis of section ordering for shop m_portland_8671
"""
import struct
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

decompressor = SaveFileDecompressor()
save_path = Path("/saves/Darkside/1767631838/data")
data = decompressor.decompress(save_path)

print("=" * 80)
print("DETAILED SECTION ORDERING ANALYSIS: m_portland_8671")
print("=" * 80)
print()

# Find shop position
shop_pattern = "itext_m_portland_8671".encode("utf-16-le")
shop_pos = data.find(shop_pattern)

print(f"Shop ID position: {shop_pos} (0x{shop_pos:08x})")
print()

# Search backwards for all section markers
search_start = max(0, shop_pos - 5000)
chunk = data[search_start:shop_pos]

# Find all section markers with their positions
markers = [
    (b".garrison", chunk.rfind(b".garrison")),
    (b".items", chunk.rfind(b".items")),
    (b".shopunits", chunk.rfind(b".shopunits")),
    (b".spells", chunk.rfind(b".spells")),
    (b".temp", chunk.rfind(b".temp"))
]

# Convert to absolute positions and sort
sections = []
for marker, rel_pos in markers:
    if rel_pos != -1:
        abs_pos = search_start + rel_pos
        sections.append((marker, abs_pos))

sections.sort(key=lambda x: x[1])

print("SECTION ORDER (from earliest to latest):")
print()
for i, (marker, pos) in enumerate(sections):
    print(f"{i+1}. {marker.decode():12s} at {pos:8d} (0x{pos:08x})")

print()
print("=" * 80)
print("CRITICAL FINDING")
print("=" * 80)
print()

# Find .spells and .shopunits positions
spells_pos = None
shopunits_pos = None
temp_pos = None

for marker, pos in sections:
    if marker == b".spells":
        spells_pos = pos
    elif marker == b".shopunits":
        shopunits_pos = pos
    elif marker == b".temp":
        temp_pos = pos

print(f".spells section:    {spells_pos} (0x{spells_pos:08x})")
print(f".shopunits section: {shopunits_pos} (0x{shopunits_pos:08x})")
print(f".temp section:      {temp_pos} (0x{temp_pos:08x})")
print(f"Shop ID:            {shop_pos} (0x{shop_pos:08x})")
print()

if spells_pos and shopunits_pos and spells_pos < shopunits_pos:
    print("ISSUE IDENTIFIED:")
    print(f"  .spells section comes BEFORE .shopunits section!")
    print(f"  Distance: {shopunits_pos - spells_pos} bytes")
    print()
    print("The current parser uses this logic:")
    print("  1. Find .shopunits section")
    print("  2. Find .spells section")
    print("  3. Parse .shopunits from shopunits_pos to spells_pos")
    print()
    print("But when .spells comes BEFORE .shopunits:")
    print("  - shopunits_pos to spells_pos is NEGATIVE or INVALID range!")
    print("  - Parser likely uses: units_pos to (spells_pos if spells_pos else shop_pos)")
    print("  - This gives: {shopunits_pos} to {shop_pos if not spells_pos else spells_pos}")
    print()

# Check what the parser is actually doing
print("=" * 80)
print("PARSER LOGIC ANALYSIS")
print("=" * 80)
print()

print("From ShopInventoryParser._parse_shop() lines 397-400:")
print()
print("  if units_pos:")
print("      next_pos = spells_pos if spells_pos else shop_pos")
print("      actual_end = self._find_section_end(data, units_pos, next_pos)")
print("      result[units] = self._parse_slash_separated(data, units_pos, actual_end)")
print()

if shopunits_pos and spells_pos:
    next_pos = spells_pos if spells_pos else shop_pos
    print(f"Given:")
    print(f"  units_pos = {shopunits_pos}")
    print(f"  spells_pos = {spells_pos}")
    print(f"  shop_pos = {shop_pos}")
    print()
    print(f"Calculation:")
    print(f"  next_pos = spells_pos if spells_pos else shop_pos")
    print(f"  next_pos = {next_pos}")
    print()
    
    # Simulate _find_section_end
    SECTION_MARKERS = {b".items", b".spells", b".shopunits", b".garrison", b".temp"}
    search_area = data[shopunits_pos:next_pos]
    earliest_marker_pos = next_pos
    
    for marker in SECTION_MARKERS:
        pos = search_area.find(marker, 1)  # Start from 1 to skip current marker
        if pos != -1:
            absolute_pos = shopunits_pos + pos
            earliest_marker_pos = min(earliest_marker_pos, absolute_pos)
    
    print(f"  _find_section_end() searches from {shopunits_pos} to {next_pos}")
    print(f"  Searching for next section marker...")
    print(f"  actual_end = {earliest_marker_pos}")
    print()
    
    if earliest_marker_pos < shopunits_pos:
        print("  ERROR: actual_end is BEFORE units_pos!")
        print("  This means the parser would parse ZERO bytes or negative range!")
    elif earliest_marker_pos == next_pos:
        print("  PROBLEM: No section marker found between units_pos and spells_pos")
        print(f"  Parser would search from {shopunits_pos} to {next_pos}")
        print(f"  BUT spells_pos < shopunits_pos, so this is backwards!")

print()
print("=" * 80)
print("ROOT CAUSE")
print("=" * 80)
print()
print("The parser assumes section order is:")
print("  .garrison -> .items -> .shopunits -> .spells -> shop_id")
print()
print("But in this save file, the actual order is:")
print("  .spells -> .shopunits -> .temp -> shop_id")
print()
print("The parser calculates:")
print("  next_pos = spells_pos if spells_pos else shop_pos")
print("  next_pos = {spells_pos} (WRONG! Should be temp_pos or shop_pos)")
print()
print("Since spells_pos ({spells_pos}) < shopunits_pos ({shopunits_pos}):")
print("  The range [shopunits_pos, spells_pos] is INVALID")
print("  Parser likely returns empty list due to invalid range")
print()

print("=" * 80)
print("VERIFICATION: What data exists in .shopunits section?")
print("=" * 80)
print()

if shopunits_pos:
    # Extract data from .shopunits to .temp (correct range)
    correct_end = temp_pos if temp_pos else shop_pos
    shopunits_data = data[shopunits_pos:correct_end]
    
    print(f"Extracting .shopunits data from {shopunits_pos} to {correct_end}")
    print(f"Size: {len(shopunits_data)} bytes")
    print()
    
    # Look for strg marker
    strg_pos = shopunits_data.find(b"strg")
    if strg_pos != -1:
        print(f"Found strg marker at offset {strg_pos}")
        str_len = struct.unpack("<I", shopunits_data[strg_pos + 4:strg_pos + 8])[0]
        str_content = shopunits_data[strg_pos + 8:strg_pos + 8 + str_len].decode("ascii")
        print(f"Content: {str_content}")
        print()
        print("UNITS FOUND:")
        parts = str_content.split("/")
        i = 0
        while i < len(parts) - 1:
            unit_name = parts[i]
            unit_qty = parts[i + 1]
            print(f"  - {unit_name}: {unit_qty}")
            i += 2

