# Actor ID Extraction from King's Bounty Save Files

## Problem

ShopInventoryParser was missing shops without `itext_` identifiers. Specifically, a shop in dragondor with bocman x1460 inventory had no in-game name and didn't display on the map, but was fully interactable.

The shop was initially identified as `dragondor_building_trader_31`, but the user indicated it should be `dragondor_actor_807991996` based on the trader's localization data.

## Discovery Process

### Initial Approach (Failed)
Attempted to use a lookup table found at position 2,160,000-2,180,000 in the save file. This table had entries like:
```
building_trader@818 se 807991996
```

However, this mapping was **incorrect** - building_trader@818 actually has actor_1906201168, not actor_807991996.

### Breakthrough Discovery

Found that actor IDs are stored in `.actors` sections **BEFORE** the inventory sections, not in a lookup table.

#### Structure
```
.actors section
  └─ strg field (4-byte value with encoded actor ID)
.shopunits section
.spells section
.temp section
lt tag (location)
building_trader@{num}
```

#### Encoding Pattern

Actor IDs are encoded in the `strg` field with **bit 7 set** in the last byte:

```
strg value: 0xb028fabc = [bc, fa, 28, b0]
actor_id:   0x3028fabc = [bc, fa, 28, 30]
            ^^^^^^^^^^^^^^^^^^^^^^^^
            First 3 bytes match exactly

Last byte:  0xb0 = 10110000 (binary)
            0x30 = 00110000 (binary)
                   ^
                   Bit 7 cleared
```

**Extraction Algorithm:**
```python
def extract_actor_id_from_strg(strg_value):
    strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))

    # Check if bit 7 is set (active shop)
    if (strg_bytes[3] & 0x80) == 0:
        return None  # Inactive/template shop

    # Clear bit 7 of last byte
    actor_bytes = list(strg_bytes)
    actor_bytes[3] = actor_bytes[3] & 0x7F

    actor_id = struct.unpack('<I', bytes(actor_bytes))[0]
    return actor_id
```

## Bit 7 Significance

Analysis of 105 shops revealed:

| Status | Count | Has Inventory | Interpretation |
|--------|-------|---------------|----------------|
| Bit 7 SET | 79 | 59/79 (74.7%) | **Active shops** with assigned actors |
| Bit 7 NOT SET | 26 | 3/26 (11.5%) | **Inactive/template** shops |

**Key Finding:** 20 shops share the value `0x3b84bcee` (actor_998554862) with NO inventory - this is a default placeholder for uninitialized shops.

## Verification Results

### Test Cases

**building_trader@31** (dragondor):
- `.actors` position: 669357 (before inventory)
- `strg` value: 0xb028fabc
- **Extracted actor ID: 807991996** ✓
- Inventory: bocman x1460, monstera x250, bear_white x156, demonologist x134

**building_trader@818** (m_inselburg):
- `.actors` position: 739118
- `strg` value: 0xf19e5250
- **Extracted actor ID: 1906201168** ✓
- This proves the lookup table was incorrect

### Parser Update

Updated `ShopInventoryParser2.py`:

1. **Removed:** `_build_trader_id_map()` - unreliable lookup table method
2. **Added:** `_extract_actor_id_from_actors_section()` - extracts from `.actors` strg field
3. **Updated:** Shop ID format:
   - Active shops: `{location}_actor_{actor_id}` (e.g., `dragondor_actor_807991996`)
   - Inactive shops: `{location}_building_trader_{building_num}` (e.g., `dragondor_building_trader_31`)

### Test Results

Parsing save file `/app/tests/game_files/saves/1768403991`:
- Total shops: 371
- **Success:** dragondor shop correctly identified as `dragondor_actor_807991996`
- Inventory verified: bocman x1460, monstera x250, bear_white x156, demonologist x134

## Conclusion

Actor IDs for building_trader@ shops are:
1. Stored in `.actors` sections BEFORE inventory
2. Encoded in `strg` field with bit 7 set in last byte
3. Extracted by clearing bit 7 when set
4. Bit 7 indicates shop is active/spawned vs inactive/template

The lookup table at 2.16M-2.18M is outdated/incorrect and should NOT be used.

## Files Modified

- `src/utils/parsers/save_data/ShopInventoryParser2.py`
  - Added `_extract_actor_id_from_actors_section()` method
  - Removed `_build_trader_id_map()` method
  - Updated shop ID format in docstrings

## Research Files Created

Directory: `tests/research/save_decompiler/kb_shop_extractor/2026-01-15/`

- `verify_actor_extraction.py` - Verified extraction algorithm
- `extract_818_actor.py` - Proved lookup table was wrong
- `analyze_bit7_pattern.py` - Analyzed bit 7 significance
- `test_multiple_shops.py` - Tested extraction across 15 shops
- `test_updated_parser.py` - Final verification of updated parser
- `SOLUTION_SUMMARY.md` - This document
