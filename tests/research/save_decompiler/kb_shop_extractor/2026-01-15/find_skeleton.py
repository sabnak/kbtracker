#!/usr/bin/env python3
"""Search for skeleton in decompressed save file - looking for skeleton/70/zombie pattern"""

from pathlib import Path
import re

# Load decompressed data
data_file = Path(__file__).parent / 'decompressed_data.bin'
with open(data_file, 'rb') as f:
    data = f.read()

print(f"Loaded {len(data)} bytes")
print()

# Search for skeleton/70/zombie pattern (the inventory user said belongs to m_portland_dark_6533)
pattern = b'skeleton/70/zombie'
positions = []
pos = 0
while True:
    pos = data.find(pattern, pos)
    if pos == -1:
        break
    positions.append(pos)
    pos += 1

print(f"Found {len(positions)} occurrences of 'skeleton/70/zombie'")
print()

# For each occurrence
for i, pos in enumerate(positions):
    print(f"{'=' * 80}")
    print(f"Occurrence {i+1} at position {pos}")
    print(f"{'=' * 80}")

    # Show 1000 bytes before
    start = max(0, pos - 1000)
    before = data[start:pos]

    # Show 1000 bytes after
    end = min(len(data), pos + 1000)
    after = data[pos:end]

    # Look for itext_ patterns in before
    try:
        text_before = before.decode('utf-16-le', errors='ignore')
        itext_matches = list(re.finditer(r'itext_([-\w]+)_(\d+)', text_before))
        if itext_matches:
            print(f"\nFound {len(itext_matches)} itext_ patterns BEFORE skeleton:")
            for match in itext_matches[-3:]:  # Show last 3
                print(f"  - {match.group(0)}")
        else:
            print("\nNo itext_ patterns found BEFORE skeleton")

        building_matches = list(re.finditer(r'building_\w+@\d+', text_before))
        if building_matches:
            print(f"\nFound {len(building_matches)} building_ patterns BEFORE skeleton:")
            for match in building_matches[-3:]:
                print(f"  - {match.group(0)}")

        if 'm_portland_dark' in text_before:
            print("\n'm_portland_dark' found BEFORE skeleton")

    except Exception as e:
        print(f"Error decoding before: {e}")

    # Look for patterns after
    try:
        text_after = after.decode('utf-16-le', errors='ignore')
        itext_matches = list(re.finditer(r'itext_([-\w]+)_(\d+)', text_after))
        if itext_matches:
            print(f"\nFound {len(itext_matches)} itext_ patterns AFTER skeleton:")
            for match in itext_matches[:3]:
                print(f"  - {match.group(0)}")

        building_matches = list(re.finditer(r'building_\w+@\d+', text_after))
        if building_matches:
            print(f"\nFound {len(building_matches)} building_ patterns AFTER skeleton:")
            for match in building_matches[:3]:
                print(f"  - {match.group(0)}")

        if 'm_portland_dark' in text_after:
            print("\n'm_portland_dark' found AFTER skeleton")

    except Exception as e:
        print(f"Error decoding after: {e}")

    # Show the full inventory line
    end_of_line = data.find(b'\x00\x00', pos, pos + 200)
    if end_of_line != -1:
        inventory = data[pos:end_of_line].decode('ascii', errors='ignore')
        print(f"\nFull inventory: {inventory}")

    print()
