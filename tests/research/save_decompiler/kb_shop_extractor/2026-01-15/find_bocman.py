#!/usr/bin/env python3
"""Search for bocman in decompressed save file and show surrounding context"""

from pathlib import Path
import re

# Load decompressed data
data_file = Path(__file__).parent / 'decompressed_data.bin'
with open(data_file, 'rb') as f:
    data = f.read()

print(f"Loaded {len(data)} bytes")
print()

# Find all occurrences of 'bocman'
bocman_positions = []
pos = 0
while True:
    pos = data.find(b'bocman', pos)
    if pos == -1:
        break
    bocman_positions.append(pos)
    pos += 1

print(f"Found {len(bocman_positions)} occurrences of 'bocman'")
print()

# For each occurrence, show context
for i, pos in enumerate(bocman_positions):
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
            print(f"\nFound {len(itext_matches)} itext_ patterns BEFORE bocman:")
            for match in itext_matches[-3:]:  # Show last 3
                print(f"  - {match.group(0)} at relative position {match.start()}")
        else:
            print("\nNo itext_ patterns found BEFORE bocman")

        # Look for building_ patterns
        building_matches = list(re.finditer(r'building_\w+@\d+', text_before))
        if building_matches:
            print(f"\nFound {len(building_matches)} building_ patterns BEFORE bocman:")
            for match in building_matches[-3:]:  # Show last 3
                print(f"  - {match.group(0)} at relative position {match.start()}")

        # Look for dragondor
        if b'dragondor' in before or 'dragondor' in text_before:
            print("\n'dragondor' found BEFORE bocman")

    except Exception as e:
        print(f"Error decoding before: {e}")

    # Look for patterns after
    try:
        text_after = after.decode('utf-16-le', errors='ignore')
        itext_matches = list(re.finditer(r'itext_([-\w]+)_(\d+)', text_after))
        if itext_matches:
            print(f"\nFound {len(itext_matches)} itext_ patterns AFTER bocman:")
            for match in itext_matches[:3]:  # Show first 3
                print(f"  - {match.group(0)} at relative position {match.start()}")

        building_matches = list(re.finditer(r'building_\w+@\d+', text_after))
        if building_matches:
            print(f"\nFound {len(building_matches)} building_ patterns AFTER bocman:")
            for match in building_matches[:3]:  # Show first 3
                print(f"  - {match.group(0)} at relative position {match.start()}")

        if b'dragondor' in after or 'dragondor' in text_after:
            print("\n'dragondor' found AFTER bocman")

    except Exception as e:
        print(f"Error decoding after: {e}")

    # Show raw context around bocman (ASCII representation)
    print(f"\nRaw context (200 bytes before, 200 after):")
    context_start = max(0, pos - 200)
    context_end = min(len(data), pos + 200)
    context = data[context_start:context_end]

    # Try to show readable parts
    readable = []
    i = 0
    while i < len(context):
        # Check if ASCII printable
        if 32 <= context[i] <= 126:
            readable.append(chr(context[i]))
        else:
            readable.append('.')
        i += 1

    print(''.join(readable))
    print()
