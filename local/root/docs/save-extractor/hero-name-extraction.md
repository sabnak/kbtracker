# Hero Name Extraction

## Overview

`HeroSaveParser` extracts hero character names from King's Bounty save files to generate unique campaign identifiers. Campaign IDs are computed as `MD5(first_name + "|" + second_name)`.

## Implementation

### Source File
`src/utils/parsers/save_data/HeroSaveParser.py`

### Data Source
Hero names are extracted from the **info file** (not the data file).

Save files contain two types of files:
- **`data` / `savedata`**: Compressed game state (slcb + zlib)
- **`info` / `saveinfo`**: Uncompressed metadata (raw binary)

### Info File Format

The info file uses a simple key-value structure:

```
[field_name_length: uint32 LE] [field_name: ASCII] [value_length: uint32 LE] [value: UTF-16LE]
```

**Hero Name Fields:**
- `name` - Hero first name (UTF-16LE encoded)
- `nickname` - Hero second name/epithet (UTF-16LE encoded, optional)

**Important**: The `value_length` field contains the **character count**, not byte count. Since UTF-16LE uses 2 bytes per character, multiply by 2 to get the actual byte length.

### Example Structure

```
Position in file:
...
[0x04][0x00][0x00][0x00]  ← field name length = 4
[n][a][m][e]               ← field name = "name"
[0x0C][0x00][0x00][0x00]  ← value length = 12 characters
[UTF-16LE data, 24 bytes]  ← hero name (12 chars × 2 bytes)
[0x04][0x00][0x00][0x00]  ← next field...
[r][a][n][k]
...
```

### Usage Example

```python
from pathlib import Path
from src.utils.parsers.save_data.HeroSaveParser import HeroSaveParser

parser = HeroSaveParser()
result = parser.parse(Path("/path/to/save"))

print(result['first_name'])   # e.g., "Неолина"
print(result['second_name'])  # e.g., "Очаровательная" or ""
```

### Hero Naming Conventions

**Single-name heroes:**
- Orc campaigns: "Зачарованная", "Справедливая", "Отважная"
- `nickname` field is absent or empty
- `second_name` returns empty string

**Two-name heroes:**
- Human campaigns: "Даэрт де Мортон", "Неолина Очаровательная"
- `nickname` field contains second name
- `second_name` returns the second name

## Campaign Identification

Campaign IDs are stable across all saves from the same campaign:

```python
import hashlib

campaign_id = hashlib.md5(
    f"{first_name}|{second_name}".encode('utf-8')
).hexdigest()
```

**Examples:**
- Single name: `MD5("Зачарованная|")` → unique ID for this orc campaign
- Two names: `MD5("Даэрт|де Мортон")` → unique ID for this human campaign

## Why Info File Instead of Data File?

**Previous approach** (deprecated):
- Scanned compressed data file for UTF-16LE Cyrillic byte patterns
- Used heuristics and keyword filtering
- 60% accuracy - captured item/unit names as hero names

**Current approach**:
- Reads structured info file with explicit `name` and `nickname` fields
- 100% accuracy - no false positives
- 50% less code, much simpler

## Related Files

- `SaveFileDecompressor.py` - Extracts info file (returns raw bytes, no decompression)
- `DataFileType.py` - Enum for DATA vs INFO file types
- `IHeroSaveParser.py` - Interface definition

## Testing

Test saves located in:
- `/tests/game_files/saves_archive/` - .sav archives (zipped)
- `/tests/game_files/saves/` - Save directories

**Test command:**
```bash
docker exec kbtracker_app bash -c 'h /app/tests/game_files/saves_archive/orcs_endgame.sav'
```

**Expected output:**
```json
{"first_name": "Зачарованная", "second_name": ""}
```

## Research

Full research documentation: `/tests/research/save_decompiler/kb_hero_extractor/2026-01-14/`

- Format analysis and discovery process
- Comparison between info file and data file approaches
- Test results and validation
