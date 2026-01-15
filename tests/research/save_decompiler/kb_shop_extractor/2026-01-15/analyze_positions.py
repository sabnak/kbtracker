#!/usr/bin/env python3
"""Analyze the area between m_portland_dark_6533 and bocman inventory"""

from pathlib import Path
import re

# Load decompressed data
data_file = Path(__file__).parent / 'decompressed_data.bin'
with open(data_file, 'rb') as f:
    data = f.read()

print("Looking for structure around m_portland_dark_6533 and bocman\n")

# Find skeleton inventory (belongs to m_portland_dark_6533)
skeleton_pos = data.find(b'skeleton/70/zombie')
print(f"skeleton/70/zombie at position: {skeleton_pos}")

# Find itext_m_portland_dark_6533
portland_itext = b'itext_m_portland_dark_6533'
portland_pos = data.find(portland_itext, skeleton_pos)
print(f"itext_m_portland_dark_6533 at position: {portland_pos}")

# Find bocman inventory
bocman_inv = b'bocman/1460/monstera/250'
bocman_pos = data.find(bocman_inv)
print(f"bocman/1460/monstera inventory at position: {bocman_pos}")

print(f"\nDistance from skeleton to portland_itext: {portland_pos - skeleton_pos} bytes")
print(f"Distance from portland_itext to bocman: {bocman_pos - portland_pos} bytes")

# Check what's between portland_itext and bocman
print(f"\n{'=' * 80}")
print(f"Analyzing region between portland_itext ({portland_pos}) and bocman ({bocman_pos})")
print(f"{'=' * 80}\n")

region = data[portland_pos:bocman_pos]

# Try UTF-16-LE decode
try:
    text = region.decode('utf-16-le', errors='ignore')

    # Look for any itext_ patterns
    itext_matches = list(re.finditer(r'itext_([-\w]+)_(\d+)', text))
    if itext_matches:
        print(f"Found {len(itext_matches)} itext_ patterns in region:")
        for match in itext_matches:
            print(f"  - {match.group(0)}")
    else:
        print("NO itext_ patterns found between portland_itext and bocman!")

    # Look for building_ patterns
    building_matches = list(re.finditer(r'building_\w+@\d+', text))
    if building_matches:
        print(f"\nFound {len(building_matches)} building_ patterns in region:")
        for match in building_matches:
            print(f"  - {match.group(0)}")

    # Look for dragondor
    if 'dragondor' in text:
        print("\n'dragondor' found in region!")
        drag_matches = list(re.finditer(r'dragondor[^\s]*', text))
        for match in drag_matches:
            print(f"  - {match.group(0)}")

    # Look for location tags (lt pattern)
    lt_matches = list(re.finditer(r'lt\s+(\w+)', text))
    if lt_matches:
        print(f"\nFound {len(lt_matches)} location tags (lt) in region:")
        for match in lt_matches:
            print(f"  - lt {match.group(1)}")

    # Look for .shopunits
    if b'.shopunits' in region:
        units_pos = region.find(b'.shopunits')
        print(f"\n.shopunits marker found at offset {units_pos} from portland_itext")

    # Look for .spells
    if b'.spells' in region:
        spells_pos = region.find(b'.spells')
        print(f".spells marker found at offset {spells_pos} from portland_itext")

except Exception as e:
    print(f"Error: {e}")

# Show first 500 chars of decoded text
print(f"\n{'=' * 80}")
print("First 500 characters of decoded region:")
print(f"{'=' * 80}\n")
try:
    text = region.decode('utf-16-le', errors='ignore')
    print(text[:500])
except:
    print("Failed to decode")
