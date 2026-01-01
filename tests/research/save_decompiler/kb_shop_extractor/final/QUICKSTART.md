# Quick Start Guide

## 5-Minute Setup

### 1. Locate Your Save File

King's Bounty saves are in: `[Game]/saves/[timestamp]/data`

Example:
```
C:/Games/KingsBounty/saves/1767209722/data
```

### 2. Run the Extractor

```bash
python kb_shop_extractor.py path/to/saves/1767209722/data output.json
```

### 3. Done!

You now have `output.json` with all shop data.

## Example Output

```json
{
  "itext_m_portland_6820": {
    "items": [
      {"name": "addon4_3_crystal", "quantity": 4},
      {"name": "snake_ring", "quantity": 1}
    ],
    "units": [
      {"name": "bowman", "quantity": 152}
    ],
    "spells": [
      {"name": "spell_plantation", "quantity": 2}
    ],
    "garrison": []
  }
}
```

## Common Use Cases

### Find All Shops Selling an Item

```bash
# Extract first
python kb_shop_extractor.py saves/123/data shops.json

# Then search
python -c "
import json
shops = json.load(open('shops.json'))
for shop_id, shop in shops.items():
    for item in shop['items']:
        if 'crystal' in item['name']:
            print(f'{shop_id}: {item[\"name\"]} x{item[\"quantity\"]}')
"
```

### Get Shop Statistics

The extractor automatically prints statistics:
- Total shops
- Shops with content
- Total items/units/spells/garrison
- Breakdown by type

### Export for Database

The JSON format is ready for database import:

```python
import json

shops = json.load(open('shops.json'))

for shop_id, shop in shops.items():
    for item in shop['items']:
        # INSERT INTO shop_products (shop_id, type, name, qty)
        # VALUES (shop_id, 'item', item['name'], item['quantity'])
        pass
```

## Need Help?

- Full documentation: See `README.md`
- Examples: See `example_usage.py`
- Technical details: See research docs in parent directory

## Requirements

- Python 3.7+
- No external dependencies
