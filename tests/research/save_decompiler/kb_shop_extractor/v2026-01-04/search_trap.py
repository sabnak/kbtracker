"""Search for 'trap' in shop binary data"""
from pathlib import Path
import sys
import struct

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

# Decompress save file
decompressor = SaveFileDecompressor()
save_path = Path('/app/tests/game_files/saves/1707047253/data')
data = decompressor.decompress(save_path)

# Find shop
shop_id = "itext_m_atrixus_late_708"
shop_bytes = shop_id.encode('utf-16-le')
shop_pos = data.find(shop_bytes)
print(f"Shop position: {shop_pos}")

# Find .items section
items_marker = b'.items'
search_start = max(0, shop_pos - 5000)
chunk = data[search_start:shop_pos]
items_offset = chunk.rfind(items_marker)
items_pos = search_start + items_offset
print(f"Items section position: {items_pos}")

# Find next section
units_marker = b'.shopunits'
units_offset = chunk.rfind(units_marker)
units_pos = search_start + units_offset
print(f"Units section position: {units_pos}")

# Extract items section data
items_section = data[items_pos:units_pos]
print(f"Items section size: {len(items_section)} bytes")

# Search for "trap"
trap_ascii = b'trap'
positions = []
pos = 0
while pos < len(items_section):
	idx = items_section.find(trap_ascii, pos)
	if idx == -1:
		break
	positions.append(idx)
	pos = idx + 1

print(f"\nFound 'trap' at {len(positions)} positions in items section:")
for pos in positions:
	# Show context around each occurrence
	start = max(0, pos - 20)
	end = min(len(items_section), pos + 20)
	context = items_section[start:end]

	print(f"\nPosition {pos} (absolute: {items_pos + pos}):")
	print(f"  Context (hex): {context.hex()}")
	print(f"  Context (ascii): {context}")

	# Check if it's length-prefixed
	if pos >= 4:
		length_pos = pos - 4
		try:
			length = struct.unpack('<I', items_section[length_pos:length_pos+4])[0]
			if length == 4:  # "trap" is 4 characters
				print(f"  ✓ Found length prefix: {length} at position {length_pos}")
				print(f"  ✓ This appears to be a valid length-prefixed 'trap' entry!")
		except:
			pass

