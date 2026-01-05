# Changelog

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
