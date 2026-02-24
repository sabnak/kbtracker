# Documentation Update Summary - v1.5.0

**Date:** 2026-01-17
**Version:** 1.5.0

## Files Updated

### 1. CHANGELOG.md
**Added:** Version 1.5.0 section at the top
- Documented Bug #9: UTF-16-LE alignment bug fix
- Documented Bug #10: False inventory attribution fix
- Added technical details with code examples
- Included validation results and test statistics
- Referenced research documentation

### 2. README.md
**Updated:** Version information and recent updates section
- Changed version from 1.4.0 → 1.5.0
- Updated date from 2026-01-15 → 2026-01-17
- Added v1.5.0 critical bug fixes to "Recent Updates"
- Added validation results for test saves quick1768586988 and quick1768595656
- Added Bug #9 and Bug #10 to regression test list
- Added v1.5.0 entry to Version History section

### 3. LIMITATIONS.md
**Added:** Recent Fixes section at the top
- Documented UTF-16-LE alignment bug as FIXED
- Explained why the bug was particularly problematic
- Updated validation scope to reflect 4+ save files and 420+ shops
- Noted v1.5.0 as the version where this was resolved

## Key Changes

### Bug #9: UTF-16-LE Alignment Bug
**Impact:** 10-15% of shops were randomly missed
**Fix:** Decode chunks at both even and odd byte offsets
**Result:** +54 to +63 shops per save

### Bug #10: False Inventory Attribution
**Impact:** NPCs incorrectly received inventory from nearby shops
**Fix:** Apply UTF-16 alignment fix to section validation
**Result:** 2 false positives removed

### New Statistics (v1.5.0)
- **Total shops:** 420 (up from 357-367)
- **Shops with inventory:** 104 (24.8%)
- **Empty entities:** 316 (75.2%)
- **Accuracy improvement:** +12-17% shop detection

## Documentation Locations

All documentation is in `/docs/save-extractor/`:
- `README.md` - Main documentation with overview and usage
- `CHANGELOG.md` - Detailed version history and bug fixes
- `LIMITATIONS.md` - Known limitations and magic constants
- `UPDATE_SUMMARY_v1.5.0.md` - This file

Research documentation in `/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/`:
- `ALIGNMENT_BUG_ANALYSIS.md` - Root cause analysis
- `FIX_RESULTS.md` - Before/after comparison
- `SECTION_ATTRIBUTION_FIX.md` - Section validation fix details

## Status

✅ All documentation updated
✅ Version numbers consistent across all files
✅ Statistics reflect actual test results
✅ Research documentation referenced
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

- [x] Version numbers match across all files (1.5.0)
- [x] Dates match across all files (2026-01-17)
- [x] Bug numbers are consistent (Bug #9, Bug #10)
- [x] Statistics match test results (420 shops, 104 with inventory)
- [x] All cross-references are valid
- [x] Research documentation paths are correct
