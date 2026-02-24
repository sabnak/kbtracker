#!/usr/bin/env python3
from pathlib import Path

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# Count NPC_template@ occurrences
npc_templates = []
pos = 0
while True:
	pos = data.find(b"NPC_template@", pos)
	if pos == -1:
		break
	
	# Extract the number
	num_start = pos + len(b"NPC_template@")
	num_end = num_start
	while num_end < len(data) and data[num_end:num_end+1].isdigit():
		num_end += 1
	
	template_num = data[num_start:num_end].decode("latin-1")
	
	# Try to find the location (lt tag before this position)
	search_start = max(0, pos - 200)
	chunk = data[search_start:pos]
	lt_pos = chunk.rfind(b"lt")
	
	location = "unknown"
	if lt_pos != -1:
		# Read the location name after lt tag
		# Format: lt <length as uint32> <location_name>
		abs_lt = search_start + lt_pos
		loc_len_start = abs_lt + 2
		if loc_len_start + 4 <= len(data):
			import struct
			loc_len = struct.unpack("<I", data[loc_len_start:loc_len_start+4])[0]
			if loc_len < 100:  # Sanity check
				loc_name_start = loc_len_start + 4
				loc_name_end = loc_name_start + loc_len
				if loc_name_end <= len(data):
					location = data[loc_name_start:loc_name_end].decode("latin-1", errors="ignore")
	
	npc_templates.append({
		"pos": pos,
		"num": template_num,
		"location": location
	})
	
	pos += 1

print(f"Total NPC_template@ occurrences: {len(npc_templates)}\n")

# Group by location
by_location = {}
for npc in npc_templates:
	loc = npc["location"]
	if loc not in by_location:
		by_location[loc] = []
	by_location[loc].append(npc["num"])

print("Breakdown by location:")
for location in sorted(by_location.keys()):
	count = len(by_location[location])
	print(f"  {location:30s}: {count:3d} templates")

print(f"\nTotal unique locations with NPC_template@: {len(by_location)}")

# Also count building_trader@
building_traders = []
pos = 0
while True:
	pos = data.find(b"building_trader@", pos)
	if pos == -1:
		break
	building_traders.append(pos)
	pos += 1

print(f"\nFor comparison:")
print(f"  building_trader@ occurrences: {len(building_traders)}")
print(f"  NPC_template@ occurrences:    {len(npc_templates)}")
