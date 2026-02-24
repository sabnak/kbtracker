from pathlib import Path
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
import struct

decompressor = SaveFileDecompressor()
save_path = Path("/app/tests/game_files/saves/inventory1769382036")
data = decompressor.decompress(save_path)

def find_and_show_item_structure(item_name):
    """Find an item and show its structure"""
    pos = data.find(item_name.encode("ascii"))
    if pos == -1:
        print(f"  NOT FOUND")
        return

    # Show 500 bytes after the item name
    chunk = data[pos:pos+500]
    text = chunk.decode("ascii", errors="ignore")
    print(f"  Structure: {text[:200]}")

    # Check for slruck
    has_slruck = b"slruck" in chunk[:300]
    print(f"  Has 'slruck': {has_slruck}")

    # Check for count
    has_count = b"count" in chunk[:100]
    print(f"  Has 'count': {has_count}")

    return

print("=== REAL ITEMS ===\n")

print("addon3_magic_ingridients:")
find_and_show_item_structure("addon3_magic_ingridients")

print("\nkerus_sword:")
find_and_show_item_structure("kerus_sword")

print("\naddon4_orc_earth_power_ring:")
find_and_show_item_structure("addon4_orc_earth_power_ring")

print("\n\n=== NON-ITEMS (stats/markers) ===\n")

print("defense:")
find_and_show_item_structure("defense")

print("\nexperience:")
find_and_show_item_structure("experience")

print("\ncrystals:")
find_and_show_item_structure("crystals")

print("\nwife0:")
find_and_show_item_structure("wife0")

print("\ncomp1_item:")
find_and_show_item_structure("comp1_item")

print("\nslbody:")
pos = data.find(b"slbody")
if pos != -1:
    chunk = data[pos:pos+200]
    text = chunk.decode("ascii", errors="ignore")
    print(f"  Structure: {text[:100]}")
