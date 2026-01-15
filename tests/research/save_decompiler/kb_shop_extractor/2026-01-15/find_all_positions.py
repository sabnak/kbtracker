#!/usr/bin/env python3
"""Find all relevant positions in order"""

from pathlib import Path
import re

# Load decompressed data
data_file = Path(__file__).parent / 'decompressed_data.bin'
with open(data_file, 'rb') as f:
    data = f.read()

print("Finding all relevant markers in order:\n")

# Find all relevant positions
positions = []

# Find skeleton inventory
skeleton_pattern = b'skeleton/70/zombie/20/ghost2'
pos = data.find(skeleton_pattern)
if pos != -1:
    positions.append(('skeleton/70/zombie/20/ghost2', pos))

# Find all itext_m_portland_dark_6533
portland_pattern = b'itext_m_portland_dark_6533'
pos = 0
while True:
    pos = data.find(portland_pattern, pos)
    if pos == -1:
        break
    positions.append((f'itext_m_portland_dark_6533', pos))
    pos += 1

# Find bocman inventory
bocman_pattern = b'bocman/1460/monstera/250/bear_white/156/demonologist'
pos = data.find(bocman_pattern)
if pos != -1:
    positions.append(('bocman/1460/monstera/250/bear_white/156/demonologist', pos))

# Find dragondor itext patterns near these positions
dragondor_pattern = b'itext_dragondor'
pos = 660000  # Start near skeleton position
while pos < 680000:
    pos = data.find(dragondor_pattern, pos)
    if pos == -1 or pos > 680000:
        break
    # Get the full shop ID
    end = pos + 50
    chunk = data[pos:end]
    try:
        text = chunk.decode('utf-16-le', errors='ignore')
        match = re.search(r'itext_dragondor_\d+', text)
        if match:
            positions.append((match.group(0), pos))
    except:
        pass
    pos += 1

# Sort by position
positions.sort(key=lambda x: x[1])

# Display
print(f"{'Position':<15} {'Marker'}")
print(f"{'-' * 80}")
for marker, pos in positions:
    if pos >= 660000 and pos <= 680000:  # Focus on relevant region
        print(f"{pos:<15} {marker}")

print(f"\n{'*' * 80}\n")
print("Analyzing the region between positions 668000-670000:\n")

# Analyze the critical region
start = 668000
end = 670000
region = data[start:end]

# Try to find structure
try:
    text = region.decode('utf-16-le', errors='ignore')

    # Find all shop-related markers
    print("Shop identifiers:")
    for match in re.finditer(r'itext_([-\w]+)_(\d+)', text):
        abs_pos = start + match.start() * 2  # Approximate
        print(f"  {match.group(0)}")

    print("\nBuilding markers:")
    for match in re.finditer(r'building_\w+@\d+', text):
        print(f"  {match.group(0)}")

    print("\nSection markers:")
    for marker in [b'.shopunits', b'.spells', b'.items', b'.garrison']:
        pos = region.find(marker)
        if pos != -1:
            print(f"  {marker.decode('ascii')} at offset {pos} (absolute: {start + pos})")

except Exception as e:
    print(f"Error: {e}")
