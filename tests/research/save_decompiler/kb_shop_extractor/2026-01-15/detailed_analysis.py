#!/usr/bin/env python3
"""Detailed analysis of the region"""

from pathlib import Path
import re

# Load decompressed data
data_file = Path(__file__).parent / 'decompressed_data.bin'
with open(data_file, 'rb') as f:
    data = f.read()

print("Detailed structure analysis:\n")

# Find key positions
skeleton_pos = data.find(b'skeleton/70/zombie/20/ghost2')
bocman_pos = data.find(b'bocman/1460/monstera/250/bear_white/156/demonologist')

print(f"skeleton inventory at: {skeleton_pos}")
print(f"bocman inventory at: {bocman_pos}")
print(f"Distance: {bocman_pos - skeleton_pos} bytes\n")

# Analyze region between them
region_start = skeleton_pos - 500
region_end = bocman_pos + 500
region = data[region_start:region_end]

print(f"{'=' * 80}")
print(f"Region from {region_start} to {region_end}")
print(f"{'=' * 80}\n")

# Find ALL occurrences of key patterns in this region
patterns_to_find = [
    (b'itext_', 'itext_*'),
    (b'building_', 'building_*'),
    (b'.shopunits', '.shopunits'),
    (b'.spells', '.spells'),
    (b'.items', '.items'),
    (b'.garrison', '.garrison'),
    (b'dragondor', 'dragondor'),
]

findings = []

for pattern, name in patterns_to_find:
    pos = 0
    while True:
        pos = region.find(pattern, pos)
        if pos == -1:
            break
        abs_pos = region_start + pos

        # Try to get the full identifier
        if pattern in [b'itext_', b'building_']:
            chunk = region[pos:pos+100]
            try:
                text = chunk.decode('utf-16-le', errors='ignore')
                if pattern == b'itext_':
                    match = re.match(r'itext_([-\w]+)_(\d+)', text)
                    if match:
                        findings.append((abs_pos, f"ITEXT: {match.group(0)}"))
                elif pattern == b'building_':
                    match = re.match(r'building_\w+@\d+', text)
                    if match:
                        findings.append((abs_pos, f"BUILDING: {match.group(0)}"))
            except:
                pass
        else:
            findings.append((abs_pos, f"MARKER: {pattern.decode('ascii', errors='ignore')}"))

        pos += 1

# Sort findings by position
findings.sort()

# Display timeline
print("Timeline of markers:\n")
for pos, desc in findings:
    offset_from_skeleton = pos - skeleton_pos
    print(f"{pos:>10}  (skeleton+{offset_from_skeleton:>5})  {desc}")

print(f"\n{skeleton_pos:>10}  (skeleton+{0:>5})  ** SKELETON INVENTORY **")
print(f"{bocman_pos:>10}  (skeleton+{bocman_pos-skeleton_pos:>5})  ** BOCMAN INVENTORY **")

# Try to decode the text between skeleton and bocman
print(f"\n{'=' * 80}")
print("Text between skeleton and bocman (UTF-16-LE decode):")
print(f"{'=' * 80}\n")

between = data[skeleton_pos:bocman_pos]
try:
    text = between.decode('utf-16-le', errors='ignore')
    # Show first 1000 chars
    print(text[:1000])
except Exception as e:
    print(f"Error: {e}")
