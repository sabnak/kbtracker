#!/usr/bin/env python3
"""
Analyze shop binary data for m_portland_6671 and m_portland_8671
"""
import struct
import re
from pathlib import Path

# Decompress save file
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

decompressor = SaveFileDecompressor()
save_path = Path("/saves/Darkside/1767631838/data")
data = decompressor.decompress(save_path)

print(f"Decompressed size: {len(data):,} bytes")
print()

# Find shop positions
def find_shop(data: bytes, shop_id: str) -> int:
    """Find shop position in UTF-16 LE encoding"""
    shop_pattern = f"itext_m_{shop_id}".encode("utf-16-le")
    pos = data.find(shop_pattern)
    return pos

# Analyze both shops
shops_to_analyze = ["portland_6671", "portland_8671"]

for shop_id in shops_to_analyze:
    print("=" * 80)
    print(f"SHOP: {shop_id}")
    print("=" * 80)
    
    shop_pos = find_shop(data, shop_id)
    if shop_pos == -1:
        print(f"ERROR: Shop not found!")
        continue
    
    print(f"Shop ID position: {shop_pos} (0x{shop_pos:08x})")
    print()
    
    # Search backwards for section markers
    search_start = max(0, shop_pos - 5000)
    chunk = data[search_start:shop_pos]
    
    sections = {
        b".garrison": chunk.rfind(b".garrison"),
        b".items": chunk.rfind(b".items"),
        b".shopunits": chunk.rfind(b".shopunits"),
        b".spells": chunk.rfind(b".spells"),
        b".temp": chunk.rfind(b".temp")
    }
    
    print("Section markers found (relative to search_start):")
    for marker, pos in sorted(sections.items(), key=lambda x: x[1] if x[1] != -1 else -999999):
        if pos != -1:
            abs_pos = search_start + pos
            print(f"  {marker.decode():12s} at {abs_pos:8d} (0x{abs_pos:08x}) - distance from shop: {shop_pos - abs_pos} bytes")
    print()
    
    # Search for unit names (pirat, pirat2, bocman, sea_magess) around shopunits section
    units_section_pos = sections[b".shopunits"]
    if units_section_pos != -1:
        units_abs_pos = search_start + units_section_pos
        print(f"Analyzing .shopunits section at {units_abs_pos}...")
        
        # Extract 1000 bytes after .shopunits marker
        units_data = data[units_abs_pos:units_abs_pos + 1000]
        
        # Look for "strg" marker (slash-separated format)
        strg_pos = units_data.find(b"strg")
        if strg_pos != -1:
            print(f"  Found strg marker at offset {strg_pos}")
            # Read string length
            if strg_pos + 10 <= len(units_data):
                str_len = struct.unpack("<I", units_data[strg_pos + 4:strg_pos + 8])[0]
                print(f"  String length: {str_len}")
                
                if 0 < str_len <= 500:
                    str_content = units_data[strg_pos + 8:strg_pos + 8 + str_len]
                    try:
                        decoded = str_content.decode("ascii")
                        print(f"  String content: {decoded}")
                    except:
                        print(f"  String content (hex): {str_content.hex()}")
        else:
            print(f"  No strg marker found in first 1000 bytes")
            
        # Also search for unit names as ASCII strings
        print()
        print("  Searching for unit names in .shopunits section:")
        for unit_name in ["pirat", "pirat2", "bocman", "sea_magess"]:
            unit_bytes = unit_name.encode("ascii")
            unit_pos = units_data.find(unit_bytes)
            if unit_pos != -1:
                print(f"    Found {unit_name} at offset {unit_pos}")
            else:
                print(f"    NOT found: {unit_name}")
    else:
        print("WARNING: No .shopunits section found!")
    
    print()
    
    # Check spells section
    spells_section_pos = sections[b".spells"]
    if spells_section_pos != -1:
        spells_abs_pos = search_start + spells_section_pos
        print(f"Analyzing .spells section at {spells_abs_pos}...")
        
        # Check if .temp marker exists between .spells and shop ID
        temp_section_pos = sections[b".temp"]
        if temp_section_pos != -1:
            temp_abs_pos = search_start + temp_section_pos
            if spells_abs_pos < temp_abs_pos < shop_pos:
                print(f"  WARNING: .temp section at {temp_abs_pos} exists between .spells and shop ID!")
                print(f"  .spells range: {spells_abs_pos} to {temp_abs_pos} ({temp_abs_pos - spells_abs_pos} bytes)")
        
        # Extract spells section data
        if temp_section_pos != -1 and search_start + temp_section_pos > spells_abs_pos:
            spells_end = search_start + temp_section_pos
        else:
            spells_end = shop_pos
        
        spells_data = data[spells_abs_pos:spells_end]
        print(f"  Spells section size: {len(spells_data)} bytes")
        
        # Look for spell names
        print("  Searching for spell identifiers:")
        spell_pattern = re.compile(b"spell_[a-z_]+")
        matches = spell_pattern.findall(spells_data)
        if matches:
            unique_spells = set()
            for match in matches:
                try:
                    spell_name = match.decode("ascii")
                    unique_spells.add(spell_name)
                except:
                    pass
            for spell in sorted(unique_spells):
                print(f"    {spell}")
        else:
            print("    No spell identifiers found")
    
    print()

print()
print("=" * 80)
print("GLOBAL SEARCH FOR UNIT NAMES")
print("=" * 80)

# Search entire save file for unit names
for unit_name in ["pirat", "pirat2", "bocman", "sea_magess"]:
    unit_bytes = unit_name.encode("ascii")
    positions = []
    pos = 0
    while True:
        pos = data.find(unit_bytes, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    
    print(f"{unit_name:12s}: Found {len(positions)} occurrences")
    if len(positions) > 0 and len(positions) <= 10:
        for p in positions:
            # Show context
            context_start = max(0, p - 20)
            context_end = min(len(data), p + len(unit_name) + 20)
            context = data[context_start:context_end]
            print(f"  Position {p:8d} (0x{p:08x}): {context.hex()}")

