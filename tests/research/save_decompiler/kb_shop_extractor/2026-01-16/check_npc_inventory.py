#!/usr/bin/env python3
from pathlib import Path

decompressed_file = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin")
with open(decompressed_file, "rb") as f:
	data = f.read()

# Find all NPC_template@ positions
npc_templates = []
pos = 0
while True:
	pos = data.find(b"NPC_template@", pos)
	if pos == -1:
		break
	npc_templates.append(pos)
	pos += 1

print(f"Checking {len(npc_templates)} NPC_template@ entries for inventory sections...\n")

# For each NPC_template@, check if there are inventory sections before it
templates_with_inventory = 0
section_counts = {
	".items": 0,
	".shopunits": 0,
	".spells": 0,
	".garrison": 0
}

for npc_pos in npc_templates:
	# Search backwards up to 3000 bytes for inventory sections
	search_start = max(0, npc_pos - 3000)
	chunk = data[search_start:npc_pos]
	
	has_inventory = False
	sections_found = []
	
	for section in [b".items", b".shopunits", b".spells", b".garrison"]:
		if section in chunk:
			sections_found.append(section.decode())
			section_counts[section.decode()] += 1
			has_inventory = True
	
	if has_inventory:
		templates_with_inventory += 1

print(f"NPC_template@ entries with inventory sections: {templates_with_inventory} / {len(npc_templates)}")
print(f"Percentage: {templates_with_inventory * 100 / len(npc_templates):.1f}%\n")

print("Section occurrence counts:")
for section, count in sorted(section_counts.items()):
	print(f"  {section:15s}: {count:3d}")

print(f"\nEstimated missing shops with inventory: {templates_with_inventory}")
