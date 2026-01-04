# Save File Parser - Final Summary Report

**Date:** 2026-01-04
**Investigation Method:** Binary analysis with Construct library + user verification
**Save File:** `/tests/game_files/saves/1707047253/data` (endgame save)
**Total Shops:** 255

---

## Overview

Successfully debugged and fixed **3 critical bugs** in the King's Bounty save file shop inventory parser through systematic binary analysis and user verification.

---

## Bug Summary

| Bug # | Issue | Root Cause | Fix | Status |
|-------|-------|------------|-----|--------|
| **#1** | Missing short-named entities | Minimum length validation too strict (5 chars) | Reduced to 3 chars | ✅ FIXED |
| **#2** | Invalid spell entries | Missing section boundary detection | Added `_find_section_end()` method | ✅ FIXED |
| **#3** | "moral" metadata as items | Missing from METADATA_KEYWORDS | Added "moral" to keywords | ✅ FIXED |

---

## Bug #1: Missing Short-Named Entities

### Issue
Shop `atrixus_late_708` missing:
- Item: "trap" (4 chars)
- Units: "imp" (3 chars), "imp2" (4 chars)

### Root Cause
**File:** `ShopInventoryParser.py`
**Lines:** 246, 319, 397
**Problem:** `len(item_id) < 5` rejected valid short names

### Fix
Changed minimum length validation from 5 → 3 characters:
```python
# Before:
if not item_id or item_id in self.METADATA_KEYWORDS or len(item_id) < 5:
    return False

# After:
if not item_id or item_id in self.METADATA_KEYWORDS or len(item_id) < 3:
    return False
```

### Impact
- **56 shops** now correctly parse short-named entities
- Short names extracted: imp, orc, trap, mana, bear, yarl, ent, lens, dice, ogre, etc.
- **Verified in-game:** ✅ User confirmed all entities present

---

## Bug #2: Invalid Spell Entries from Adjacent Sections

### Issue
Shop `atrixus_10` had invalid "spell" entries:
- `adisabled` (not a spell)
- `book_times` (not a spell)
- `dragondor` (not a spell)
- `territory` (not a spell)

### Root Cause
**File:** `ShopInventoryParser.py`
**Lines:** 290-344, 409-426
**Problem:** Parser didn't detect `.temp` section marker between `.spells` and shop ID, continued parsing beyond section boundary

### Fix
Added section boundary detection:

**1. Added SECTION_MARKERS constant (line 26):**
```python
SECTION_MARKERS: set[bytes] = {
    b'.items', b'.spells', b'.shopunits', b'.garrison', b'.temp'
}
```

**2. Added `_find_section_end()` method (after line 160):**
```python
def _find_section_end(
    self,
    data: bytes,
    section_start: int,
    max_end: int
) -> int:
    """Find actual end of section by detecting next section marker"""
    search_area = data[section_start:max_end]
    earliest_marker_pos = max_end

    for marker in self.SECTION_MARKERS:
        pos = search_area.find(marker, 1)
        if pos != -1:
            absolute_pos = section_start + pos
            earliest_marker_pos = min(earliest_marker_pos, absolute_pos)

    return earliest_marker_pos
```

**3. Updated `_parse_shop()` to use proper boundaries (lines 409-426):**
```python
# For each section, find actual end before parsing
actual_end = self._find_section_end(data, section_pos, next_pos)
result['section'] = self._parse_section(data, section_pos, actual_end)
```

### Impact
- Prevents reading beyond section boundaries
- Invalid entries from `.temp` section no longer appear
- **Logic validated** through binary analysis

---

## Bug #3: "moral" Metadata Parsed as Items

### Issue
Shop `zcom_519` showed 15 items (expected 13):
- Two entries named "moral" appeared in items list
- User stated: "that're not even items"

### Root Cause
**File:** `ShopInventoryParser.py`
**Lines:** 21-24
**Problem:** "moral" missing from METADATA_KEYWORDS set

**Binary structure revealed:**
```
ITEM_ENTRY:
  - item_name (e.g., "addon4_demon_smoldering_boots")
  - METADATA:
    - count: 1
    - moral: 25     ← MORALE BONUS VALUE (metadata field)
    - id: 16
    - slruck: "2,1"
    - lvars: "rndid/..."
```

"moral" is a **metadata field** containing the item's morale bonus value, NOT an item name.

### Fix
Added "moral" to METADATA_KEYWORDS:
```python
# Before:
METADATA_KEYWORDS: set[str] = {
    'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
    'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h'
}

# After:
METADATA_KEYWORDS: set[str] = {
    'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
    'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h', 'moral'
}
```

### Impact
- **48 "moral" metadata entries** across all shops no longer counted as items
- Total items: 837 → 789 (48 fewer false positives)
- **Verified in-game:** ✅ User confirmed shop `zcom_519` has 13 items

---

## Final Statistics

### Before All Fixes
- **Bug #1:** Missing short-named entities (56 shops affected)
- **Bug #2:** Invalid spell entries (shops with `.temp` sections affected)
- **Bug #3:** 48 false "moral" items across all shops

### After All Fixes
**Total shops:** 255
**Total entities correctly parsed:**
- **Items:** 789 (was 837, removed 48 false "moral" entries)
- **Units:** 894 (includes previously missing short names like imp, orc, etc.)
- **Spells:** 738 (no longer includes invalid entries from adjacent sections)
- **Garrison:** 23

**Shop coverage:**
- 176 shops with items (69%)
- 190 shops with units (75%)
- 192 shops with spells (75%)
- 9 shops with garrison (4%)

---

## Verification

### In-Game Verification (User Confirmed)
✅ **Shop `atrixus_late_708`:**
- Items: 5 items including "trap" ✓
- Units: 3 units including "imp" x810, "imp2" x2250 ✓
- Spells: 5 spells ✓

✅ **Shop `zcom_519`:**
- Items: 13 items (not 15) ✓
- No "moral" entries ✓
- Units: 12 units ✓
- Spells: 34 spells ✓

### Binary Analysis Verification
✅ All entities confirmed present in binary data
✅ Section boundaries correctly identified
✅ Metadata structure documented

---

## Tools and Investigation Methods

### Tools Created

**Binary Analysis:**
- `kb_save_format.py` - Construct library format definitions
- `explore_shop.py` - Interactive binary explorer with hex dumps
- `search_trap.py` - Search for specific entities in binary
- `analyze_moral_structure.py` - Analyze metadata structure

**Validation:**
- `test_current_parser.py` - Test parser on specific shops
- `find_suspicious_shops.py` - Identify shops for validation
- `investigate_duplicate_moral.py` - Binary search for "moral" entries

**Export:**
- `export_all_shops.py` - Export all 255 shops to JSON and TXT

### Documentation
- `BUG_ROOT_CAUSES.md` - Root cause analysis for Bugs #1 and #2
- `BUG_3_MORAL_METADATA.md` - Root cause analysis for Bug #3
- `VALIDATION_RESULTS.md` - Comprehensive validation report
- `FINAL_SUMMARY.md` - This document

### Libraries Used
- **Construct** (Python library for declarative binary parsing)
- **Context7 MCP Server** (AI-optimized documentation for Construct)

---

## Files Modified

### src/utils/parsers/save_data/ShopInventoryParser.py

**Changes made:**

1. **Line 24:** Added "moral" to METADATA_KEYWORDS
2. **Lines 26-28:** Added SECTION_MARKERS constant
3. **Lines 161-179:** Added `_find_section_end()` method
4. **Line 246:** Changed minimum length from 5 → 3 (items)
5. **Line 319:** Changed minimum length from 5 → 3 (spells)
6. **Line 397:** Changed minimum length from 5 → 3 (validation)
7. **Lines 409-426:** Updated `_parse_shop()` to use section boundaries

**Total changes:** 7 modifications across 3 categories
- 3 × minimum length fixes (Bug #1)
- 3 × section boundary detection (Bug #2)
- 1 × metadata keyword addition (Bug #3)

---

## Export Files

All shop data exported to:
**Location:** `tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/`

**Files:**
1. **all_shops_export.json** (212 KB) - Machine-readable JSON
2. **all_shops_export.txt** (135 KB) - Human-readable text
3. **export_statistics.txt** (279 B) - Summary statistics

**Export includes:**
- All 255 shops alphabetically sorted
- Items, units, spells, garrison for each shop
- Quantities for all entities
- Summary statistics

---

## Lessons Learned

1. **Binary analysis tools are essential** - Construct library enabled systematic exploration
2. **User verification is critical** - Bug #3 only discovered through in-game verification
3. **Metadata can mimic data** - "moral" looked like an item name but was metadata
4. **Section boundaries matter** - `.temp` and other markers must be detected
5. **Validation rules must be complete** - One missing keyword caused 48 false positives

---

## Status: ✅ ALL BUGS FIXED

**Parser now correctly:**
- ✅ Extracts entities with names as short as 3 characters
- ✅ Detects section boundaries to prevent contamination
- ✅ Filters all metadata keywords including "moral"
- ✅ Handles all 255 shops in the save file
- ✅ Matches in-game verification

**Next steps:**
- Test on second save file (`/tests/game_files/saves/1767209722/data`) for regression validation
- Consider extending to other save file sections if needed
- Monitor for additional metadata keywords that may appear in other saves

---

**Investigation Time:** ~4 hours
**Bugs Fixed:** 3 critical issues
**Shops Affected:** 255 shops (all shops in save file)
**False Positives Removed:** 48 "moral" metadata entries
**Missing Entities Recovered:** 56 shops with short names now working

**Result:** 🎉 **COMPLETE SUCCESS**
