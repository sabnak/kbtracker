# Changelog

## Version 1.5.0 (2026-01-17)

### Critical Bug Fixes

**Bug #9: UTF-16-LE Alignment Bug - Missing Shops at Odd Byte Offsets**
- **Issue:** Shops located at odd byte offsets within chunks were not detected, causing ~10-15% of shops to be randomly missed
- **Example:** `m_inselburg_6529` found in one save but missing in another (same shop, different byte position)
- **Root Cause:** Parser decoded UTF-16-LE data only at even byte offsets (0), missing shops at odd offsets (1)
- **Impact Before Fix:**
  - Save `quick1768586988`: 357 shops extracted (missing 54 shops, ~13% loss)
  - Save `quick1768595656`: 367 shops extracted (missing 44 shops, ~11% loss)
- **Fix:** Decode chunks at BOTH even and odd byte offsets (alignment_offset in [0, 1])
- **Impact After Fix:**
  - Both saves: **420 shops** extracted (+54 and +44 shops respectively)
  - 104 shops with inventory (items/units/spells/garrison)
  - 316 empty shops (NPCs and entities without inventory)
- **Affected Methods:**
  - `_find_all_shop_ids()` - Shop detection (lines 157-217)
  - `_section_belongs_to_shop()` - Section attribution validation (lines 655-693)

**Bug #10: False Inventory Attribution - Section Reuse Across Shops**
- **Issue:** Inventory sections incorrectly attributed to multiple shops
- **Example:** `m_whitehill_1725` (enemy NPC) received spells from `m_zcom_1308` (real shop 1484 bytes before)
- **Root Cause:** `_section_belongs_to_shop()` had same UTF-16 alignment bug - couldn't detect intervening shops at odd offsets
- **Fix:** Apply UTF-16 alignment fix to section validation
- **Impact:**
  - Removed 2 false positives: `m_whitehill_1725`, `m_castle_of_monteville_1205`
  - Corrected empty NPCs now show as truly empty
  - More accurate shop/NPC distinction

### Technical Details

**UTF-16-LE Alignment Issue:**
```python
# Problem: Shop text at odd offset gets misaligned during UTF-16-LE decoding
Chunk starts at byte 107800 (even)
Shop at byte 113773 (odd offset within chunk = 5973)
→ UTF-16-LE decode reads byte pairs: [5972,5973], [5974,5975], [5976,5977]...
→ Shop text "itext_m_inselburg_6529" split incorrectly → garbage characters
→ Regex fails to match → shop not found

# Solution: Try both alignments
for alignment_offset in [0, 1]:
    decode_start = pos + alignment_offset
    text = data[decode_start:decode_end].decode('utf-16-le', errors='ignore')
    matches = re.finditer(r'itext_([-\w]+)_(\d+)', text)
```

**Why This Happened:**
- Save files evolve during gameplay (items collected, spells learned, etc.)
- New content shifts all subsequent data by varying byte amounts
- Same shop can appear at even offset in one save, odd offset in another
- Without alignment fix: probabilistic ~50% detection rate per shop

**Affected Saves:**
- `quick1768586988` and `quick1768595656` differ by **661 bytes**
- Content changes: spells learned (`dark_light_energy_3`, `enemy_units_leadership5`, etc.)
- Time difference: 144.5 minutes of gameplay between saves
- Shop shifted from byte 113773 (odd, missed) to 113658 (even, found)

### Validation

**Test Results:**
| Save File | Before Fix | After Fix | Change |
|-----------|-----------|-----------|--------|
| quick1768586988 | 357 shops | 420 shops | +63 (+17.6%) |
| quick1768595656 | 367 shops | 420 shops | +53 (+14.4%) |

**Shop Statistics (After Fix):**
- Total shops: 420
- Shops with inventory: 104 (24.8%)
- Empty shops: 316 (75.2% - NPCs, entities)
- Shops with items: 98
- Shops with units: 96
- Shops with spells: 96
- Shops with garrison: 7

**Verification:**
✅ `m_inselburg_6529` now found in both saves with correct inventory:
  - Items: addon2_belt_obeliks_belt, astral_bow
  - Units: pirat2 x2580, robber x2140, assassin x300, spider_venom x9000, spider_fire x9200
  - Spells: advspell_summon_bandit, titan_sword, fire_arrow

✅ `m_whitehill_1725` (enemy NPC) now correctly shows empty inventory (no false spells)

✅ Tests passed: `tests/smoke/test_shop_inventory_parser.py`

### Research Documentation

- Full investigation: `/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/`
- `ALIGNMENT_BUG_ANALYSIS.md` - Complete root cause analysis with hex dumps
- `FIX_RESULTS.md` - Before/after comparison and test results
- `SECTION_ATTRIBUTION_FIX.md` - False inventory attribution fix details

### Performance Impact

- **Parsing time:** +5-10% (due to double decoding per chunk)
- **Memory usage:** No significant change
- **Accuracy improvement:** +12-17% more shops extracted

### Breaking Changes

None - all changes are backward compatible

---

## Version 1.4.0 (2026-01-15)

### Major Features

**Feature: Actor ID Extraction for building_trader@ Shops**
- **New Capability:** Extract actor IDs from shops without `itext_` identifiers
- **Shop Types Supported:**
  1. Standard named shops: `{location}_{shop_num}` (e.g., `m_portland_8671`)
  2. Actor-based shops: `{location}_actor_{actor_id}` (e.g., `dragondor_actor_807991996`)
- **Filtering:** Only active shops with actor IDs (bit 7 set) are included
- **Impact:** Correctly identifies shops with trader actors for proper naming/localization

**Actor ID Extraction Method:**
- Actor IDs stored in `.actors` section before inventory
- Encoded in `strg` field with **bit 7 set** in last byte
- Extraction algorithm:
  ```python
  # Clear bit 7 of last byte to extract actor ID
  actor_bytes[3] = strg_bytes[3] & 0x7F
  ```
- Example encoding:
  ```
  strg value: 0xb028fabc = [bc, fa, 28, b0]  (bit 7 = 1)
  actor_id:   0x3028fabc = [bc, fa, 28, 30]  (bit 7 = 0)
  Difference: 0xb0 → 0x30 (bit 7 cleared: 0x80)
  ```

**Bit 7 Significance:**
- **Bit 7 SET (75% of shops):** Active shops with assigned actors
- **Bit 7 NOT SET (25% of shops):** Inactive/template shops without actors
- Default placeholder value: `0x3b84bcee` (actor_998554862) for uninitialized shops

### Technical Details

**Building Trader Shop Structure:**
```
.actors section          ← Contains encoded actor ID in 'strg' field
  └─ strg field with bit 7 set
.shopunits section       ← Units for hire
.spells section          ← Spells for purchase
.items section           ← Items for sale
.temp section            ← Temporary metadata
lt tag                   ← Location name (ASCII)
building_trader@{num}    ← Shop identifier (ASCII)
```

**Extraction Process:**
1. Find `building_trader@{num}` marker
2. Search backwards for `.actors` section (within 3000 bytes)
3. Locate `strg` field (offset +8 from 'strg' marker)
4. Read 4-byte little-endian value
5. Check if bit 7 is set in last byte
6. If set: Clear bit 7 to extract actor ID and include shop
7. If not set: Shop is inactive, skip it entirely

**Examples:**
- `dragondor_actor_807991996` - Active shop with trader (bocman x1460 inventory)
- `m_inselburg_actor_1906201168` - Active shop with different trader
- Inactive shops without actors are skipped (not included in results)

### Removed Features

**Deprecated Lookup Table Method:**
- ❌ Removed `_build_trader_id_map()` method
- Reason: Lookup table at position 2.16M-2.18M contained outdated/incorrect mappings
- Example error: Mapped `building_trader@818` → `actor_807991996` (incorrect, actual: `actor_1906201168`)

### Validation

**Tested on:**
- Save /saves/1768403991: 371 shops extracted
- `dragondor_actor_807991996` correctly identified with bocman x1460 inventory
- `m_inselburg_actor_1906201168` correctly identified (not 807991996)
- 79 active shops with bit 7 set (74.7% have inventory)
- 26 inactive shops without bit 7 (11.5% have inventory)

**Verification Results:**
```
✓ dragondor_actor_807991996:
  - bocman x1460
  - monstera x250
  - bear_white x156
  - demonologist x134
```

**Research Documentation:**
- Full investigation: `tests/research/save_decompiler/kb_shop_extractor/2026-01-15/`
- `SOLUTION_SUMMARY.md` - Complete discovery process and algorithm
- Verification scripts for extraction algorithm
- Bit 7 pattern analysis across 105 shops

### Breaking Changes

None - all changes are backward compatible. Shops with `itext_` identifiers work exactly as before.

---

## Version 1.3.1 (2026-01-06)

### Critical Bug Fixes

**Bug #8: Shop ID Truncation and Inventory Loss**
- **Issue:** Shop IDs with multi-digit numbers being truncated, causing 98% inventory loss
- **Example:** `m_zcom_start_519` parsed as both `m_zcom_start_519` AND `m_zcom_start_5` (truncated)
- **Root Causes:**
  1. **Chunk Boundary Split:** UTF-16-LE shop IDs split across 10KB chunk boundaries during parsing
  2. **Duplicate Shop IDs:** Same shop_id appearing at multiple binary positions, with later (empty) occurrences overwriting earlier (populated) ones
- **Fix:** Implemented overlapping chunks with dual deduplication
  - 200-byte overlap between chunks (3x safety margin over longest shop ID: 66 bytes)
  - `seen_positions` set: Prevents overlap duplicates
  - `seen_shop_ids` set: Prevents duplicate shop IDs at different positions
- **Impact:**
  - Before fix: 312 shops, 4 with content (98% empty), 39 total products
  - After fix: 312 shops, 72 with content, 943 total products (24x increase)
  - Inventory breakdown: 10 garrison units, 385 items, 323 units, 225 spells
- **Affected Code:** `_find_all_shop_ids()` method in `ShopInventoryParser.py` (lines 72-120)

### Technical Details

**Chunk Boundary Split Bug:**
```
Chunk 1 end:   ...itext_m_zcom_start_5|
Chunk 2 start:                        |19_terr...
                                      └─ Split at byte 530000
```
When shop ID `itext_m_zcom_start_519_terr` falls across chunk boundary:
- Chunk 1 decodes as: `itext_m_zcom_start_5` (truncated)
- Chunk 2 decodes as: `19_terr>` (remainder)
- Both point to same binary position but have different shop_id values

**Duplicate Shop IDs Bug:**
```
Position 2792807: "aralan_2944" (has inventory data)
Position 2793004: "aralan_2944" (empty)
```
When building result dict, later occurrence overwrites earlier:
- 112 shop IDs appeared at 2+ positions (428 total occurrences → 312 unique IDs)
- Later occurrences often contained empty inventory data
- Result: 98% of shops lost their inventory content

### Validation

**Tested on:**
- Save /saves/Darkside/1767650305: 312 shops correctly identified
- 72 shops with content (23% utilization)
- 943 total products extracted successfully
- No duplicate shop IDs
- No truncated shop IDs

**Verification Scripts:**
- `verify_fix.py` - Confirms overlapping chunks work correctly
- `analyze_byte_lengths.py` - Validates 200-byte overlap provides 3x safety margin
- `check_duplicates.py` - Confirms no duplicate shop IDs remain

**Research Documentation:**
- Full investigation: `F:\var\kbtracker\tests\research\save_decompiler\kb_shop_extractor\2026-01-06\`
- Executive summary with visual diagrams
- Binary forensics analysis
- Step-by-step bug reproduction

### Breaking Changes

None - all changes are backward compatible

---

## Version 1.3.0 (2026-01-05)

### Critical Bug Fixes

**Bug #5: Missing Units in Shops with Out-of-Order Sections**
- **Issue:** Shops with sections in non-standard order (e.g., .spells before .units) had missing units
- **Example:** `m_portland_8671` was missing 4 units
- **Root Cause:** Parser assumed sections appeared in fixed order (garrison → items → units → spells)
- **Fix:** Implemented section order independence - sections now parsed in any order
- **Impact:** All shops correctly extract units regardless of section ordering

**Bug #6: False Positive Spells from Other Shops**
- **Issue:** Spells from adjacent shops incorrectly attributed to current shop
- **Root Cause:** Backward section search could cross shop boundaries
- **Fix:** Added `_section_belongs_to_shop()` verification method
- **Impact:** Eliminated cross-shop section attribution

**Bug #7: "mana" and "limit" Metadata Appearing as Items**
- **Issue:** Metadata fields "mana" and "limit" treated as item names
- **Example:** `dragondor_5464` had false "mana" and "limit" items
- **Fix:** Added "mana" and "limit" to METADATA_KEYWORDS filter list
- **Impact:** Cleaner output, no false positive items

### Validation

Tested on multiple save files with correct results.

### Breaking Changes

None - all changes are backward compatible

---

## Version 1.2.0 (2026-01-05)

### Critical Bug Fixes

**Bug #4: Shops Without "m_" Prefix Not Extracted**
- **Issue:** Entire locations missing from exports (aralan, dragondor, d) - shops without "m_" prefix not detected
- **Example:** `itext_aralan_3338` and 58 other shops were not extracted
- **Root Cause:** Regex pattern `r'itext_m_\w+_\d+'` required "m_" prefix, plus hardcoded string slicing assumed 8-character prefix
- **Fix:** Updated to universal pattern `r'itext_([-\w]+)_(\d+)'` using capture groups for location and shop number
- **Impact:** 59 additional shops discovered across 3 locations
  - aralan: 25 shops
  - dragondor: 16 shops
  - d: 18 shops
- **Affected Code:** Line 122 in `ShopInventoryParser.py` - `_find_all_shop_ids()` method

### Statistics Update (Save 1707047253)

**Before v1.2.0 (v1.1.0):**
- Total shops: 255
- Total items: 789
- Total units: 894
- Total spells: 738
- Total garrison: 23

**After v1.2.0:**
- Total shops: 314 (+59)
- Total items: 882 (+93)
- Total units: 994 (+100)
- Total spells: 828 (+90)
- Total garrison: 29 (+6)

### Validation

**Bug #4 Regression Test:**
- ✅ Shop `aralan_3338` successfully extracted
- ✅ 59 previously missing shops now found
- ✅ All existing shops still work correctly
- ✅ Pattern supports hyphens in location names

### Breaking Changes

None - all changes are backward compatible

---

## Version 1.1.0 (2026-01-04)

### Critical Bug Fixes

**Bug #1: Short-Named Entities Not Extracted**
- **Issue:** Entities with names < 5 characters were filtered out (imp, trap, orc, mana, bear, etc.)
- **Root Cause:** Minimum length validation was set to 5 characters
- **Fix:** Reduced minimum length from 5 → 3 characters in `_is_valid_id()` method
- **Impact:** 56 shops now correctly extract short-named entities
- **Affected Code:** Lines 246, 319, 397 in `ShopInventoryParser.py`

**Bug #2: Invalid Entries from Adjacent Sections**
- **Issue:** Parser read beyond section boundaries into `.temp` and other adjacent sections
- **Root Cause:** No section boundary detection - parser assumed shop ID marked end of section
- **Fix:** Added `_find_section_end()` method with SECTION_MARKERS detection
- **Impact:** No more invalid entries appearing in parsed data
- **Affected Code:** Added SECTION_MARKERS constant (line 26), `_find_section_end()` method (after line 160), updated `_parse_shop()` (lines 409-426)

**Bug #3: "moral" Metadata Appearing as Items**
- **Issue:** "moral" metadata field (morale bonus value) treated as item name
- **Root Cause:** "moral" missing from METADATA_KEYWORDS filter list
- **Fix:** Added "moral" to METADATA_KEYWORDS set
- **Impact:** Reduced total items from 837 → 789 (48 false positives removed across all shops)
- **Affected Code:** Line 24 in `ShopInventoryParser.py`

### New Features

- ✅ Universal console export tool (`export_shop_inventory.py`)
- ✅ Multiple output formats (JSON, TXT, stats)
- ✅ Timestamped exports to `/tmp/save_export/`
- ✅ Validated on 2 save files (endgame + early game)

### Documentation Updates

- ✅ Updated `README.md` with v1.1.0 changes
- ✅ Updated `QUICKSTART.md` with Docker-based usage
- ✅ Updated `PRODUCTION_READY.md` with bug fixes and validation status
- ✅ Added comprehensive research documentation in `tests/research/`

### Validation

**Tested on:**
- Save 1707047253 (Endgame): 255 shops, 789 items, 894 units, 738 spells
- Save 1767209722 (Early Game): 247 shops, 243 items, 209 units, 124 spells

**Bug Regression Tests:**
- Bug #1: ✅ 10 short-named entities found
- Bug #2: ✅ No invalid entries
- Bug #3: ✅ 0 "moral" items

### Breaking Changes

None - all changes are backward compatible

### Known Issues

- Missing automated regression tests
- No production logging
- Smoke test has DI container configuration issues

---

## Version 1.0.0 (2025-12-31)

### Initial Release

- ✅ Save file decompression (zlib)
- ✅ Shop inventory extraction (4 sections: garrison, items, units, spells)
- ✅ Correct quantity parsing for all section types
- ✅ Metadata keyword filtering
- ✅ JSON export
- ✅ Complete documentation

### Known Issues (Fixed in v1.1.0)

- ❌ Minimum 5 character validation too strict
- ❌ No section boundary detection
- ❌ "moral" metadata not filtered
