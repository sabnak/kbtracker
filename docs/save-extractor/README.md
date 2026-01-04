# King's Bounty Shop Inventory Extractor

**Version:** 1.1.0
**Date:** 2026-01-04
**Status:** Production Ready ✅

## Overview

Production-ready tool to extract shop inventory data from King's Bounty save files. Extracts all shop contents including items, units, spells, and garrison across all game locations.

## Recent Updates (v1.1.0)

**Critical Bug Fixes:**
- ✅ **Bug #1 Fixed:** Short-named entities (imp, trap, orc, mana) now correctly extracted (minimum 3 chars, was 5)
- ✅ **Bug #2 Fixed:** Section boundary detection prevents invalid entries from adjacent sections
- ✅ **Bug #3 Fixed:** "moral" metadata no longer appears as items

**Improvements:**
- ✅ Validated on multiple save files (endgame + early game)
- ✅ Universal console tool with standardized output
- ✅ Comprehensive documentation of binary format

## Features

- ✅ Extracts all 4 shop sections: Garrison, Items, Units, Spells
- ✅ Handles correct quantity parsing for all item types
- ✅ Filters metadata keywords automatically (including "moral")
- ✅ Exports to JSON, TXT, and statistics files
- ✅ Validated on multiple save files (255 shops endgame, 247 shops early game)
- ✅ Integrated with project dependency injection
- ✅ Proper section boundary detection

## Requirements

- Python 3.14+
- Docker container (kbtracker_app)
- Project dependencies (see Container)

## Installation

No installation needed - tool is part of the project at:
```
src/utils/parsers/save_data/export_shop_inventory.py
```

## Usage

### Docker Container Usage

```bash
docker exec kbtracker_app python src/utils/parsers/save_data/export_shop_inventory.py <save_path>
```

### Arguments

- `save_path` - Absolute path to King's Bounty save 'data' file inside container (required)

### Examples

**Extract endgame save:**
```bash
docker exec kbtracker_app python src/utils/parsers/save_data/export_shop_inventory.py /app/tests/game_files/saves/1707047253/data
```

**Extract early game save:**
```bash
docker exec kbtracker_app python src/utils/parsers/save_data/export_shop_inventory.py /app/tests/game_files/saves/1767209722/data
```

### Output Location

All exports are saved to: `/tmp/save_export/` inside container

Files created (with timestamp):
- `{save_name}_{timestamp}.json` - Machine-readable JSON
- `{save_name}_{timestamp}.txt` - Human-readable text
- `{save_name}_{timestamp}_stats.txt` - Summary statistics

## Save File Location

King's Bounty saves are typically located in:
- **Game Directory:** `[Game Install]/saves/[timestamp]/data`

Each save is a directory with a timestamp (e.g., `1707047253`) containing:
- `data` - Main save file (use this as input)
- `info` - Save metadata
- `name` - Save name
- `crc` - Checksum

## Output Format

### JSON Format

```json
{
  "portland_6820": {
    "garrison": [],
    "items": [
      {"name": "addon4_3_crystal", "quantity": 4},
      {"name": "snake_ring", "quantity": 1}
    ],
    "units": [
      {"name": "bowman", "quantity": 152}
    ],
    "spells": [
      {"name": "spell_plantation", "quantity": 2},
      {"name": "spell_sanctuary", "quantity": 2}
    ]
  }
}
```

### TXT Format

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

### JSON Fields

- **Shop ID** (key): Unique shop identifier (e.g., `portland_6820`)
- **garrison**: Player's stored army units (array of name/quantity objects)
- **items**: Equipment and consumable items for sale (array)
- **units**: Units/troops available for hire (array)
- **spells**: Spells available for purchase (array)

Each item/unit/spell contains:
- `name`: Item identifier (e.g., `addon4_3_crystal`, `bowman`, `spell_lull`)
- `quantity`: Available quantity

## How It Works

### Save File Format

King's Bounty save files use the following structure:

```
Header (12 bytes):
  - 4 bytes: Magic "slcb"
  - 4 bytes: Compressed size (uint32 LE)
  - 4 bytes: Decompressed size (uint32 LE)

Body:
  - N bytes: zlib compressed data
```

### Shop Structure

Each shop in the decompressed data follows this pattern:

```
[.garrison section]   ← Player's stored army (optional, 3 slots max)
[.items section]      ← Equipment and consumables for sale
[.shopunits section]  ← Units/troops for hire
[.spells section]     ← Spells for purchase
[.temp section]       ← Temporary metadata (optional)
[Shop ID UTF-16 LE]   ← Identifier: "itext_m_<location>_<number>"
```

**Important:** Section boundary detection prevents parsing data from adjacent sections (Bug #2 fix).

### Quantity Storage

Different sections use different formats for storing quantities:

#### 1. ITEMS Section
**Format:** Quantity stored in `slruck` metadata field
**Structure:** `[length][name][metadata...slruck[length]["slot,quantity"]...]`
**Example:** `slruck....2,4` means slot 2, quantity 4

```python
# Items can be:
# - Stackable consumables (crystals, potions): quantity > 1
# - Non-stackable equipment (armor, weapons): quantity = 1
```

#### 2. SPELLS Section
**Format:** Quantity as first uint32 after name
**Structure:** `[length][name][quantity][next spell...]`

```python
# Spell scrolls can stack
# Quantity stored directly after spell name
```

#### 3. UNITS & GARRISON Sections
**Format:** Slash-separated string
**Structure:** `"unit_name/quantity/unit_name/quantity/..."`
**Example:** `"bowman/152/knight/25"`

```python
# Units and garrison use the same format
# Stored as ASCII string with "/" separators
```

### Extraction Process

1. **Decompress** - Extract zlib compressed data
2. **Find Shops** - Scan for shop IDs (UTF-16 LE pattern matching)
3. **Locate Sections** - Search backwards from shop ID for section markers
4. **Detect Boundaries** - Find actual section end using SECTION_MARKERS
5. **Parse Each Section** - Use appropriate parser for each section type
6. **Validate IDs** - Filter out metadata keywords
7. **Export** - Save to JSON, TXT, and stats files

## Validation

The extractor has been validated on multiple save files:

### Save 1707047253 (Endgame)
- **Shops:** 255 total
- **Items:** 789 total
- **Units:** 894 total
- **Spells:** 738 total
- **Garrison:** 23 total
- **Coverage:** 69% items, 75% units, 75% spells
- **Status:** ✅ PASS

### Save 1767209722 (Early Game)
- **Shops:** 247 total
- **Items:** 243 total
- **Units:** 209 total
- **Spells:** 124 total
- **Garrison:** 3 total
- **Coverage:** 17% items, 16% units, 17% spells
- **Status:** ✅ PASS

### Bug Regression Tests
- **Bug #1 (Short names):** ✅ 10 short-named entities found in early game
- **Bug #2 (Section boundaries):** ✅ No invalid entries from adjacent sections
- **Bug #3 ("moral" metadata):** ✅ 0 "moral" entries found (correctly filtered)

## Technical Details

### Metadata Keywords Filtered

These strings are metadata, not actual items:
```
count, flags, lvars, slruck, id, strg, bmd, ugid,
temp, hint, label, name, image, text, s, h, moral
```

**Note:** "moral" is a metadata field containing item morale bonus values (Bug #3 fix).

### Section Boundary Markers

```python
SECTION_MARKERS = {
    b'.items', b'.spells', b'.shopunits', b'.garrison', b'.temp'
}
```

Parser detects these markers to prevent parsing beyond section boundaries (Bug #2 fix).

### Validation Rules

Valid item/unit/spell IDs must:
- Match pattern: `^[a-z][a-z0-9_]*$`
- Be at least **3 characters long** (Bug #1 fix - was 5)
- Not be a metadata keyword

### Performance

- **Processing Speed:** ~2-5 seconds for typical save file
- **Memory Usage:** ~20-50 MB for 10 MB save file
- **Output Size:** ~200-500 KB total (JSON + TXT + stats)

## Known Issues & Limitations

### Scope Limitations
- Only extracts shop data (does not extract player inventory, quest states, etc.)
- Requires decompressed save file to be valid King's Bounty format
- Item names are internal game IDs (not localized display names)

### Fixed in v1.1.0
- ✅ Short-named entities (3-4 chars) now work correctly
- ✅ Section boundaries properly detected
- ✅ "moral" metadata no longer appears as items

### Remaining Considerations
- **Uses conservative limits** that work for normal saves but may need adjustment for:
  - Very large shops (>5KB sections)
  - Items with extensive metadata (>500 bytes)
  - Modded content with unusual formats

**See `LIMITATIONS.md` for detailed information and how to adjust constants.**

## Troubleshooting

### "Invalid save file magic"
- Ensure you're using the 'data' file, not 'info' or 'name'
- Save file may be corrupted

### "Size mismatch"
- Save file is corrupted or incomplete
- Try a different save file

### Empty or missing shops
- Save file may be from a different game version
- Check that the save is actually from King's Bounty

### Missing short-named entities (imp, trap, orc)
- **Fixed in v1.1.0** - Ensure you're using latest version
- Parser now handles names with 3+ characters

### "moral" appearing as items
- **Fixed in v1.1.0** - Ensure you're using latest version
- This was metadata being misidentified as items

## Version History

### 1.1.0 (2026-01-04)
- ✅ **Bug #1 Fixed:** Minimum name length reduced from 5 to 3 characters
- ✅ **Bug #2 Fixed:** Section boundary detection added
- ✅ **Bug #3 Fixed:** "moral" metadata keyword added to filter list
- ✅ Validated on 2 save files (endgame + early game)
- ✅ Universal console tool with standardized output
- ✅ Comprehensive bug investigation documentation

### 1.0.0 (2025-12-31)
- ✅ Initial production release
- ✅ Correct quantity parsing for all section types
- ✅ Metadata keyword filtering
- ✅ Complete documentation

## Documentation

**API Documentation:**
- `QUICKSTART.md` - 5-minute quick start guide
- `PRODUCTION_READY.md` - Production readiness assessment
- `LIMITATIONS.md` - Known limitations and adjustments
- `example_usage.py` - Programmatic usage examples

**Research Documentation:**
- `tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/BUG_ROOT_CAUSES.md` - Bug analysis
- `tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/FINAL_SUMMARY.md` - Complete investigation summary
- `tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/PRODUCTION_READINESS.md` - Production readiness details

## License

This tool was created for research and educational purposes.

---

**Developed by:** Claude (Anthropic)
**Date:** 2026-01-04
**Status:** Production Ready ✅
**Version:** 1.1.0
