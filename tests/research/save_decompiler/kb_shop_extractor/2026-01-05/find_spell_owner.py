#!/usr/bin/env python3
"""
Find which shop the .spells section at position 51681 belongs to
"""
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

decompressor = SaveFileDecompressor()
save_path = Path("/saves/Darkside/1767631838/data")
data = decompressor.decompress(save_path)

spells_pos = 51681

print(f".spells section at position: {spells_pos}")
print()

# Search backwards from .spells to find the shop ID that owns it
search_start = max(0, spells_pos - 2000)
chunk_before = data[search_start:spells_pos]

# Look for shop ID in UTF-16 LE before .spells
import re

try:
    text_before = chunk_before.decode("utf-16-le", errors="ignore")
    matches = list(re.finditer(r"itext_(m_)?([a-z_-]+)_(\d+)", text_before))
    
    if matches:
        # Get the last match (closest to .spells)
        last_match = matches[-1]
        shop_id_full = last_match.group(0)
        
        # Remove "itext_" prefix and optionally "m_" prefix
        if shop_id_full.startswith("itext_m_"):
            shop_id = shop_id_full[8:]  # Remove "itext_m_"
        elif shop_id_full.startswith("itext_"):
            shop_id = shop_id_full[6:]  # Remove "itext_"
        else:
            shop_id = shop_id_full
        
        print(f"Shop immediately BEFORE .spells section: {shop_id}")
        print(f"Full pattern: {shop_id_full}")
except Exception as e:
    print(f"Error: {e}")

print()

# Also search FORWARD from .spells to find which shop is AFTER it
search_end = min(len(data), spells_pos + 10000)
chunk_after = data[spells_pos:search_end]

try:
    text_after = chunk_after.decode("utf-16-le", errors="ignore")
    matches = list(re.finditer(r"itext_(m_)?([a-z_-]+)_(\d+)", text_after))
    
    if matches:
        print(f"Shops AFTER .spells section (in order):")
        for i, match in enumerate(matches[:10]):
            shop_id_full = match.group(0)
            
            if shop_id_full.startswith("itext_m_"):
                shop_id = shop_id_full[8:]
            elif shop_id_full.startswith("itext_"):
                shop_id = shop_id_full[6:]
            else:
                shop_id = shop_id_full
            
            # Estimate position
            byte_offset = match.start() * 2  # UTF-16 LE uses 2 bytes per char
            abs_pos = spells_pos + byte_offset
            
            print(f"  {i+1}. {shop_id} at ~{abs_pos}")
except Exception as e:
    print(f"Error: {e}")

