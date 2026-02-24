# Documentation Update Summary - v1.5.1

**Date:** 2026-01-24
**Version:** 1.5.1

## Files Updated

### 1. CHANGELOG.md
**Added:** Version 1.5.1 section at the top
- Documented Bug #11: Incorrect section attribution to itext shops
- Explained root cause with file position timeline
- Showed comparison with `_section_belongs_to_building_trader()` correct implementation
- Added before/after test results from save quick1769254717
- Included validation results showing correct shop separation
- Referenced research documentation in `/tests/research/save_decompiler/kb_shop_extractor/2026-01-24/`

### 2. README.md
**Updated:** Version information and recent updates section
- Changed version from 1.5.0 → 1.5.1
- Updated date from 2026-01-17 → 2026-01-24
- Added v1.5.1 critical bug fix to "Recent Updates"
- Added Bug #11 to regression test list
- Added v1.5.1 entry to Version History section
- Updated footer version and date

### 3. SaveDataParser.py
**Fixed:** `_section_belongs_to_shop()` method (line 655)
- Added `building_trader@` check before UTF-16-LE alignment checks
- One-line fix: `if b'building_trader@' in chunk: return False`
- Brings method to parity with `_section_belongs_to_building_trader()` logic

## Key Changes

### Bug #11: Incorrect Section Attribution to itext Shops
**Impact:** itext shops claiming inventory from preceding building_trader@ shops
**Example:** `m_zcom_start_519` merged with `building_trader@31` (actor 807991996)
**Fix:** Added `building_trader@` check to `_section_belongs_to_shop()` method
**Result:** +2 shops correctly separated (438 vs 436), accurate inventory per shop

### Test Results (Save quick1769254717)

**Before Fix:**
- Total shops: 436 (2 shops incorrectly merged)
- `m_zcom_start_519`: Showed actor 807991996 inventory (wrong)

**After Fix:**
- Total shops: 438 (correctly separated)
- `m_zcom_start_519`: Only its own units (archer, zombie, imp)
- `building_trader@31` (actor 807991996): Correct inventory (bocman, items, spells)

## Root Cause Analysis

**File Structure:**
```
718713: .actors (actor 807991996)
718769: .items       ← Actor shop inventory
719274: .spells      ← Actor shop inventory
719785: building_trader@31 (actor 807991996)
720314: .shopunits   ← m_zcom_start_519 inventory
720601: itext_m_zcom_start_519
```

**Problem:**
- Parser searched backwards from `m_zcom_start_519` (720601)
- Found `.items` (718769) and `.spells` (719274)
- Called `_section_belongs_to_shop()` to validate ownership
- Chunk 718769→720601 contained `building_trader@` but NO `itext_`
- Method only checked for `itext_`, returned True
- Result: Wrong inventory attribution

**Fix:**
```python
def _section_belongs_to_shop(self, data: bytes, section_pos: int, shop_pos: int) -> bool:
    chunk = data[section_pos:shop_pos]

    # NEW: Check for building_trader@ shops
    if b'building_trader@' in chunk:
        return False

    # Existing: Check for itext_ shops (UTF-16-LE aligned)
    # ...
```

## Documentation Locations

All documentation is in `/docs/save-extractor/`:
- `README.md` - Main documentation with overview and usage
- `CHANGELOG.md` - Detailed version history and bug fixes
- `LIMITATIONS.md` - Known limitations and magic constants
- `UPDATE_SUMMARY_v1.5.1.md` - This file

Research documentation in `/tests/research/save_decompiler/kb_shop_extractor/2026-01-24/`:
- `README.md` - Complete investigation with root cause analysis
- Decompressed save data for verification

## Status

✅ All documentation updated
✅ Version numbers consistent across all files (1.5.1)
✅ Bug fix implemented and tested
✅ Statistics reflect actual test results (438 shops)
✅ Research documentation created
✅ Production ready status maintained

## Notes for Future Updates

When updating to v1.6.0:
1. Add new version section at top of CHANGELOG.md
2. Update version and date in README.md header
3. Move current "Recent Updates" to "Previous Updates" in README.md
4. Add new version entry to Version History section
5. Update validation statistics if tests on new saves
6. Create UPDATE_SUMMARY_v1.6.0.md for tracking changes

## Validation

- [x] Version numbers match across all files (1.5.1)
- [x] Dates match across all files (2026-01-24)
- [x] Bug number is consistent (Bug #11)
- [x] Statistics match test results (438 shops, +2 from fix)
- [x] All cross-references are valid
- [x] Research documentation paths are correct
- [x] Code fix matches documentation description
- [x] Test results verified on save quick1769254717
