# King's Bounty Save File Decompiler - Research Findings

## Summary

Successfully reverse-engineered the King's Bounty save file format and extracted shop inventory data.

**Results:**
- Extracted **114 shops** with item inventories
- Found **379 unique items** across all shops
- Developed working parser to map shop IDs to item IDs

## Save File Format

### Structure

```
Offset 0x00-0x03: Magic Header "slcb" (4 bytes)
Offset 0x04-0x07: Decompressed Size (little-endian uint32)
Offset 0x08-0x0B: Compressed Size (little-endian uint32)
Offset 0x0C+:     zlib compressed data
```

### Example

```
File: /tests/game_files/saves/1707078232/data
- Magic: "slcb"
- Decompressed size: 10,811,680 bytes (10.8 MB)
- Compressed size: 1,660,088 bytes (1.66 MB)
- Compression ratio: 6.51x
```

## Decompressed Data Format

The decompressed save data uses a structured binary format with:

1. **Length-prefixed ASCII strings** for item IDs and metadata
2. **UTF-16 LE encoded strings** for shop IDs and localized text
3. **Binary metadata** (counts, flags, offsets)

### Key Patterns

#### Shop IDs (UTF-16 LE)

Shop IDs are stored with the `strg` marker followed by UTF-16 LE encoded strings:

```
4 bytes: "strg" (marker)
4 bytes: length in bytes (uint32, little-endian)
N bytes: UTF-16 LE string
```

**Example:**
- `itext_m_galenirimm_2207`
- `itext_m_helvedia_96`
- `itext_m_barazgund_3544`

**Pattern:** `itext_m_<location>_<number>`

#### Item IDs (ASCII)

Item IDs are stored WITHOUT the "itm_" prefix as ASCII strings with length prefix:

```
4 bytes: length (uint32, little-endian)
N bytes: ASCII string (item ID without "itm_" prefix)
```

**Examples:**
- `addon4_orc_primitive_sword` (stored without "itm_" prefix)
- `addon2_gauntlet_avrelii_gauntlet`
- `addon4_spell_rock_armageddon_250`

#### Shop Inventory Sections

Shop inventories are marked with `.items` section:

```
".items" marker (6 bytes)
metadata (variable length)
"strg" marker (4 bytes)
item count (4 bytes)
padding (8 bytes)
[for each item]:
    length (4 bytes)
    item_name (ASCII, <length> bytes)
    item_metadata (variable)
```

## Data Extraction Process

### Step 1: Decompress Save File

```python
import zlib
import struct

with open('save/data', 'rb') as f:
    # Read header
    magic = f.read(4)  # "slcb"
    decompressed_size = struct.unpack('<I', f.read(4))[0]
    compressed_size = struct.unpack('<I', f.read(4))[0]

    # Decompress
    compressed_data = f.read()
    decompressed_data = zlib.decompress(compressed_data)
```

### Step 2: Find Shop Sections

Search for `.items` markers in decompressed data:

```python
pos = 0
while True:
    pos = data.find(b'.items', pos)
    if pos == -1:
        break
    # Parse items at this position
    pos += 1
```

### Step 3: Parse Item Lists

After `.items` marker:
1. Skip to `strg` marker
2. Read item count (4 bytes after strg)
3. Skip 8 bytes of metadata
4. For each item:
   - Read length (4 bytes)
   - Read item name (ASCII string)
   - Skip item metadata

### Step 4: Associate with Shop

Search nearby (±16KB) for shop ID in UTF-16 format:
- Pattern: `itext_m_\w+_\d+`
- Decode as UTF-16 LE
- Find closest shop ID to items section

## Output Format

The extracted data is in JSON format:

```json
{
  "itext_m_galenirimm_2207": [
    "addon4_orc_primitive_sword",
    "addon2_gauntlet_avrelii_gauntlet"
  ],
  "itext_m_helvedia_96": [
    "addon3_weapon_grandpa_sword",
    "addon4_spell_rock_blizzard_250"
  ]
}
```

**Note:** Item IDs in save files do NOT include the "itm_" prefix. When using these IDs with the game database, prepend "itm_" to get the full item ID.

## Tools Created

### 1. `analyze_format.py`
- Analyzes save file header
- Detects and verifies zlib compression
- Decompresses save data

### 2. `search_ids.py`
- Searches for shop and item ID patterns
- Tests different encodings (ASCII, UTF-16)

### 3. `parse_shops_v2.py` ⭐ Main Tool
- Extracts all shop-to-items mappings
- Outputs JSON format
- Successfully extracted 114 shops with 379 unique items

## Key Findings

1. **Magic Header:** All save files start with "slcb"
2. **Compression:** zlib with default compression level
3. **Shop IDs:** Stored as UTF-16 LE with `strg` marker
4. **Item IDs:** Stored as ASCII WITHOUT "itm_" prefix
5. **Structure:** Binary format with `.items`, `.shopunits`, `.spells` sections
6. **Encoding Mix:** UTF-16 for localized text, ASCII for internal IDs

## Limitations

- Parser extracts ~114 shops from 582 `.items` sections
  - Some sections may be player inventory or other non-shop containers
  - Shops with no items are not included
- Item IDs require "itm_" prefix to match database
- Some complex item entries include upgrade paths: `upgrade/base_item,upgraded_item/rndid/123456`

## Next Steps

To integrate this into the main application:

1. **Create SaveFileParser utility**
   - Decompress save file
   - Extract shop inventories
   - Add "itm_" prefix to item IDs

2. **Add to database schema**
   ```sql
   CREATE TABLE shop_inventories (
       save_id VARCHAR,
       shop_id VARCHAR,
       item_id VARCHAR,
       PRIMARY KEY (save_id, shop_id, item_id)
   );
   ```

3. **UI Integration**
   - Upload save file
   - Parse and store shop inventories
   - Display shop items on location pages
   - Add "reveal shop" button to show generated inventory

## Files

- `analyze_format.py` - Format analyzer and decompressor
- `search_ids.py` - ID pattern searcher
- `parse_shops_v2.py` - **Main extraction tool**
- `shop_inventories_v2.json` - **Extracted data** (114 shops)
- `decompressed.bin` - Decompressed save data
- `FINDINGS.md` - This documentation

## Success Criteria ✅

- [x] Understand save file format
- [x] Decompress save file
- [x] Extract shop IDs
- [x] Extract item IDs
- [x] Map shops to items
- [x] Output in usable format (JSON)

**Mission Accomplished!**
