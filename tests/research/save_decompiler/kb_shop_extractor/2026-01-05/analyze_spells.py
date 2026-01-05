#!/usr/bin/env python3
"""
Analyze the spells appearing in both shops
"""
import struct
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

decompressor = SaveFileDecompressor()
save_path = Path("/saves/Darkside/1767631838/data")
data = decompressor.decompress(save_path)

print("=" * 80)
print("SPELL ANALYSIS: ARE THEY REAL OR FALSE POSITIVES?")
print("=" * 80)
print()

shops = [
    ("m_portland_6671", 55866),
    ("m_portland_8671", 56420)
]

for shop_name, shop_pos_known in shops:
    print("=" * 80)
    print(f"SHOP: {shop_name}")
    print("=" * 80)
    
    # Find shop
    shop_pattern = f"itext_{shop_name}".encode("utf-16-le")
    shop_pos = data.find(shop_pattern)
    
    print(f"Shop position: {shop_pos}")
    print()
    
    # Find sections
    search_start = max(0, shop_pos - 5000)
    chunk = data[search_start:shop_pos]
    
    spells_rel = chunk.rfind(b".spells")
    temp_rel = chunk.rfind(b".temp")
    
    if spells_rel == -1:
        print("No .spells section found")
        print()
        continue
    
    spells_pos = search_start + spells_rel
    temp_pos = search_start + temp_rel if temp_rel != -1 else None
    
    print(f".spells position: {spells_pos}")
    if temp_pos:
        print(f".temp position:   {temp_pos}")
    print(f"Shop ID:          {shop_pos}")
    print()
    
    # Determine correct end of spells section
    if temp_pos and spells_pos < temp_pos < shop_pos:
        spells_end = temp_pos
        print(f"Spells section: {spells_pos} to {spells_end} (ends at .temp)")
    else:
        spells_end = shop_pos
        print(f"Spells section: {spells_pos} to {spells_end} (ends at shop ID)")
    
    spells_data = data[spells_pos:spells_end]
    print(f"Spells section size: {len(spells_data)} bytes")
    print()
    
    # Look for the two spell names
    spell1 = b"spell_advspell_summon_bandit"
    spell2 = b"spell_advspell_summon_human"
    
    print("Searching for spell names in .spells section:")
    
    for spell_name in [spell1, spell2]:
        pos = spells_data.find(spell_name)
        if pos != -1:
            print(f"  Found {spell_name.decode()} at offset {pos}")
            
            # Check if this is a length-prefixed entry
            if pos >= 4:
                # Check for length prefix
                potential_len = struct.unpack("<I", spells_data[pos-4:pos])[0]
                if potential_len == len(spell_name):
                    print(f"    - Has valid length prefix: {potential_len}")
                    
                    # Check for quantity after name
                    if pos + len(spell_name) + 4 <= len(spells_data):
                        quantity = struct.unpack("<I", spells_data[pos+len(spell_name):pos+len(spell_name)+4])[0]
                        print(f"    - Quantity: {quantity}")
                        
                        if 0 < quantity < 10000:
                            print(f"    - Valid quantity range")
                        else:
                            print(f"    - INVALID quantity (too high or zero)")
                else:
                    print(f"    - Length prefix mismatch: {potential_len} vs {len(spell_name)}")
        else:
            print(f"  NOT found: {spell_name.decode()}")
    
    print()
    
    # Check if these spells appear OUTSIDE the spells section (in .temp or elsewhere)
    if temp_pos:
        print("Checking .temp section:")
        temp_end = shop_pos
        temp_data = data[temp_pos:temp_end]
        
        for spell_name in [spell1, spell2]:
            pos = temp_data.find(spell_name)
            if pos != -1:
                print(f"  WARNING: {spell_name.decode()} also found in .temp at offset {pos}")
    
    print()

# Check if both shops share the SAME .spells section
print()
print("=" * 80)
print("SECTION SHARING ANALYSIS")
print("=" * 80)
print()

shop1_pos = data.find("itext_m_portland_6671".encode("utf-16-le"))
shop2_pos = data.find("itext_m_portland_8671".encode("utf-16-le"))

print(f"Shop m_portland_6671 at: {shop1_pos}")
print(f"Shop m_portland_8671 at: {shop2_pos}")
print(f"Distance: {shop2_pos - shop1_pos} bytes")
print()

# Find .spells for shop 1
search1 = max(0, shop1_pos - 5000)
chunk1 = data[search1:shop1_pos]
spells1_rel = chunk1.rfind(b".spells")
spells1_pos = search1 + spells1_rel if spells1_rel != -1 else None

# Find .spells for shop 2
search2 = max(0, shop2_pos - 5000)
chunk2 = data[search2:shop2_pos]
spells2_rel = chunk2.rfind(b".spells")
spells2_pos = search2 + spells2_rel if spells2_rel != -1 else None

print(f".spells for shop 6671: {spells1_pos}")
print(f".spells for shop 8671: {spells2_pos}")
print()

if spells1_pos == spells2_pos:
    print("CRITICAL: Both shops reference the SAME .spells section!")
    print("This suggests the .spells section belongs to a DIFFERENT shop")
    print("that comes BEFORE both of these shops in the save file.")
    print()
    
    # Find which shop this .spells section actually belongs to
    print("Finding the actual shop this .spells section belongs to...")
    
    # Search forward from .spells section
    search_forward = data[spells1_pos:shop1_pos]
    
    # Look for shop ID pattern
    import re
    shop_pattern = re.compile(b"itext_(m_)?([a-z_-]+)_(\d+)", re.IGNORECASE)
    
    # Decode as UTF-16 LE
    try:
        text = search_forward.decode("utf-16-le", errors="ignore")
        matches = list(re.finditer(r"itext_(m_)?([a-z_-]+)_(\d+)", text))
        
        if matches:
            print(f"Found {len(matches)} shop IDs between .spells and shop 6671:")
            for match in matches[:5]:  # Show first 5
                print(f"  - {match.group(0)}")
    except:
        pass

