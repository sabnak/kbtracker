"""
Search for all building_trader entries and check if they have itext_ identifiers nearby
"""

with open('decompressed_data.bin', 'rb') as f:
    data = f.read()

# Find all building_trader positions
pattern = b'building_trader@'
positions = []
start = 0
while True:
    pos = data.find(pattern, start)
    if pos == -1:
        break
    positions.append(pos)
    start = pos + 1

print(f'Found {len(positions)} building_trader entries')
print()

# For each building_trader, check if itext_ appears within 1000 bytes before it
no_itext_count = 0
no_itext_shops = []

for pos in positions[:50]:  # Check first 50
    # Look 1000 bytes before
    search_start = max(0, pos - 1000)
    context = data[search_start:pos]
    
    if b'itext_' not in context:
        no_itext_count += 1
        # Extract building_trader ID
        end = pos + 50
        building_line = data[pos:end].decode('utf-8', errors='replace')
        
        # Get location tag
        lt_search = data[max(0, pos-200):pos]
        lt_pos = lt_search.rfind(b'lt')
        location = 'unknown'
        if lt_pos != -1:
            loc_data = lt_search[lt_pos:lt_pos+50].decode('utf-8', errors='replace')
            location = loc_data.split('\x00')[0].replace('lt', '').strip()
        
        no_itext_shops.append({
            'position': pos,
            'building': building_line.split('\x00')[0],
            'location': location
        })

print(f'Building_trader entries WITHOUT itext_ within 1000 bytes: {no_itext_count}')
print()

if no_itext_shops:
    print('Details:')
    for shop in no_itext_shops[:10]:
        print(f"  Position {shop['position']}: {shop['building']} in {shop['location']}")
