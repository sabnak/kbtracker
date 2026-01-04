# Quick Start Guide

**Version:** 1.2.0 | **Date:** 2026-01-05

## 5-Minute Setup

### 1. Locate Your Save File

King's Bounty saves are in: `[Game]/saves/[timestamp]/data`

Example:
```
C:/Games/KingsBounty/saves/1707047253/data
```

### 2. Run the Extractor

```bash
docker exec kbtracker_app python src/utils/parsers/save_data/export_shop_inventory.py /app/tests/game_files/saves/1707047253/data
```

### 3. Done!

Check `/tmp/save_export/` inside the container for your exports:
- `{save}_timestamp.json` - Machine-readable
- `{save}_timestamp.txt` - Human-readable
- `{save}_timestamp_stats.txt` - Statistics

## Example Usage

### Extract Endgame Save
```bash
docker exec kbtracker_app python src/utils/parsers/save_data/export_shop_inventory.py /app/tests/game_files/saves/1707047253/data
```

**Output:**
```
Parsing save file: /app/tests/game_files/saves/1707047253/data

Export complete:
  JSON: /tmp/save_export/1707047253_20260104_211453.json
  TXT:  /tmp/save_export/1707047253_20260104_211453.txt
  Stats: /tmp/save_export/1707047253_20260104_211453_stats.txt
```

### Extract Early Game Save
```bash
docker exec kbtracker_app python src/utils/parsers/save_data/export_shop_inventory.py /app/tests/game_files/saves/1767209722/data
```

## Output Format

### Statistics File
```
EXPORT STATISTICS
================================================================================

Save: 1707047253
Export date: 2026-01-04 21:14:53

Total shops: 255
Total items: 789
Total units: 894
Total spells: 738
Total garrison: 23

Shops with items: 176
Shops with units: 190
Shops with spells: 192
Shops with garrison: 9
```

### JSON Output
```json
{
  "portland_6820": {
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

### TXT Output
```
================================================================================
SHOP: portland_6820
================================================================================
Summary: 2 items, 1 units, 2 spells, 0 garrison

ITEMS (2):
  1. addon4_3_crystal x4
  2. snake_ring x1

UNITS (1):
  1. bowman x152

SPELLS (2):
  1. spell_plantation x2
  2. spell_sanctuary x2
```

## Common Use Cases

### Find All Shops Selling an Item

```bash
# 1. Extract data
docker exec kbtracker_app python src/utils/parsers/save_data/export_shop_inventory.py /app/tests/game_files/saves/1707047253/data

# 2. Copy JSON file from container
docker cp kbtracker_app:/tmp/save_export/1707047253_*.json ./shops.json

# 3. Search for items
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

Statistics are automatically exported to `*_stats.txt`:

```bash
docker exec kbtracker_app cat /tmp/save_export/1707047253_*_stats.txt
```

### Copy Exports to Host Machine

```bash
# Copy all exports
docker cp kbtracker_app:/tmp/save_export/. ./save_exports/

# Copy specific file
docker cp kbtracker_app:/tmp/save_export/1707047253_20260104_211453.json ./
```

## What's New in v1.2.0?

**Critical Bug Fix - Missing Locations:**
- ✅ **Bug #4 Fixed:** Entire locations (aralan, dragondor, d) now extracted
- ✅ **+59 shops discovered** (255 → 314 total shops)
- ✅ Example: `aralan_3338` and 58 other shops now in exports

**Previous Bug Fixes (v1.1.0):**
- ✅ Short names (imp, orc, trap) now work (was missing 3-4 char entities)
- ✅ "moral" metadata no longer appears as items
- ✅ Section boundaries properly detected (no invalid entries)

**Before v1.2.0:**
- Save 1707047253: 255 shops
- Missing: All aralan shops, dragondor shops, d shops

**After v1.2.0:**
- Save 1707047253: 314 shops (+59) ✅
- All locations extracted including aralan, dragondor, d ✅

## Troubleshooting

### "File not found" errors
- Ensure save path is absolute and inside container
- Use `/app/tests/game_files/saves/{id}/data` format

### Empty exports
- Check that save file is valid King's Bounty format
- Verify the 'data' file (not 'info' or 'name')

### Missing entities (imp, trap, orc)
- ✅ Fixed in v1.1.0 - Update to latest version

### Missing entire locations (aralan, dragondor)
- ✅ Fixed in v1.2.0 - Update to latest version

## Need Help?

- Full documentation: See `README.md`
- Examples: See `example_usage.py`
- Production readiness: See `PRODUCTION_READY.md`
- Technical details: See research docs

## Requirements

- Docker container (kbtracker_app)
- Python 3.14+ (in container)
- Valid King's Bounty save file

---

**Version:** 1.2.0
**Last Updated:** 2026-01-05
