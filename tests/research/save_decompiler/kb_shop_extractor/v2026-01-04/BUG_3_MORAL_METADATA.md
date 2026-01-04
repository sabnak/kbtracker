# Bug #3: Moral Metadata Parsed as Items

**Date:** 2026-01-04
**Discovered:** During user verification of shop `zcom_519`
**Reporter:** User noticed "moral" appearing as items but stated "that're not even items"

---

## Issue Description

**Reported Problem:**
- Shop `zcom_519` showed 15 items, but user confirmed only 13 items exist in-game
- Two entries named "moral" appeared in items list
- User explicitly stated: "that're not even items"

**Parser Output (Before Fix):**
```
Items (15):
  ...
  13. battle_talmud
  14. moral  ← NOT AN ITEM
  15. moral  ← NOT AN ITEM
```

**Expected Output:**
```
Items (13):
  1-13. [actual items only]
```

---

## Investigation

### Binary Structure Analysis

**Tool Used:** `analyze_moral_structure.py`

**Findings:**

The binary data structure for each item in `.items` section is:
```
ITEM_ENTRY:
  - item_name (length-prefixed ASCII string)
  - METADATA SECTION:
    - count: <quantity> (how many of this item)
    - moral: <morale_value> (morale bonus for item)
    - id: <internal_id>
    - slruck: <slot_rack_info>
    - lvars: <random_id>
```

**Example from hex dump:**
```
Position 815257: "addon4_demon_smoldering_boots" ← ITEM NAME
Position 815314: "count" ← metadata
  Value: 1
Position 815327: "moral" ← METADATA (morale bonus value)
  Value: 25
Position 815340: "id" ← metadata
  Value: 16
Position 815350: "slruck" ← metadata
  Value: "2,1"
Position 815367: "lvars" ← metadata
  Value: "rndid/2851645005"

Position 815400: "addon4_elf_moon_pants" ← NEXT ITEM NAME
```

**Conclusion:**
- "moral" is a **metadata field** containing the item's morale bonus value
- NOT an item name
- Appears in metadata section of EVERY item that has a morale bonus

---

## Root Cause

**File:** `src/utils/parsers/save_data/ShopInventoryParser.py`
**Line:** 21-24
**Constant:** `METADATA_KEYWORDS`

**Current Implementation (Before Fix):**
```python
METADATA_KEYWORDS: set[str] = {
    'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
    'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h'
}
```

**Problem:**
- Parser filters out metadata keywords to avoid treating them as item names
- "moral" was **NOT in the METADATA_KEYWORDS set**
- Parser treated "moral" as a valid item name

**Why Other Metadata Was Filtered:**
- "count" → in METADATA_KEYWORDS ✅ filtered
- "id" → in METADATA_KEYWORDS ✅ filtered
- "slruck" → in METADATA_KEYWORDS ✅ filtered
- "lvars" → in METADATA_KEYWORDS ✅ filtered
- "moral" → **NOT in METADATA_KEYWORDS** ❌ passed through as item

---

## Fix

**Line 21-24:**

**Before:**
```python
METADATA_KEYWORDS: set[str] = {
    'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
    'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h'
}
```

**After:**
```python
METADATA_KEYWORDS: set[str] = {
    'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
    'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h', 'moral'
}
```

**Change:** Added `'moral'` to the METADATA_KEYWORDS set

---

## Validation

### Test Case: Shop `zcom_519`

**Before Fix:**
```
Items (15):
  1. addon3_gloves_fire_gloves
  2. addon4_dead_catchy_claw
  3. addon4_dead_inception_ring
  4. addon4_demon_smoldering_boots
  5. addon4_elf_moon_pants
  6. addon4_imp_belt
  7. addon4_lizard_claw
  8. addon4_lizard_defense_ring
  9. addon4_lizard_swamp_armor_1
  10. addon4_orc_goblin_boots
  11. addon4_orc_willow_pipe
  12. addon4_undead_dark_crossbow
  13. battle_talmud
  14. moral ❌
  15. moral ❌
```

**After Fix:**
```
Items (13):
  1. addon3_gloves_fire_gloves
  2. addon4_dead_catchy_claw
  3. addon4_dead_inception_ring
  4. addon4_demon_smoldering_boots
  5. addon4_elf_moon_pants
  6. addon4_imp_belt
  7. addon4_lizard_claw
  8. addon4_lizard_defense_ring
  9. addon4_lizard_swamp_armor_1
  10. addon4_orc_goblin_boots
  11. addon4_orc_willow_pipe
  12. addon4_undead_dark_crossbow
  13. battle_talmud
```

**Status:** ✅ **FIXED AND VERIFIED**

### Test Case: Shop `whitehill_1326`

**Before Fix:**
- 14 items (including one "moral" metadata entry)

**After Fix:**
- 13 items (moral metadata correctly filtered)

**Status:** ✅ **FIXED**

### Impact on All Shops

**Before Fix:**
- Total items across all shops: 837
- Some shops had "moral" incorrectly counted as items

**After Fix:**
- Total items should be lower (exact count TBD after re-export)
- All "moral" metadata entries correctly filtered

---

## Additional Discovery

**Item Metadata Structure:**

Based on binary analysis, each item in the save file has this metadata structure:
```
ITEM:
  - name: <item_kb_id>
  - count: <quantity>        # How many in stock
  - moral: <morale_bonus>    # Morale bonus value (if applicable)
  - id: <internal_id>        # Internal item instance ID
  - slruck: <slot_rack>      # Slot/rack position info
  - lvars: <rndid/...>       # Random ID for item instance
```

**Notes:**
- Not all items have all metadata fields
- "moral" only appears for items that provide morale bonuses
- This explains why two "moral" entries appeared (two different items with morale bonuses)

---

## Lessons Learned

1. **Metadata keyword list must be comprehensive** - Missing even one keyword can cause incorrect parsing
2. **Binary structure has complex metadata** - Items aren't just name+quantity
3. **User verification is critical** - Automated tests couldn't catch this without in-game verification

---

## Files Created

**Investigation:**
- `analyze_moral_structure.py` - Binary structure analysis around "moral" entries
- `BUG_3_MORAL_METADATA.md` - This document

**Testing:**
- `test_current_parser.py` - Validates parser output before/after fix

---

## Conclusion

**Bug Type:** Incomplete metadata keyword filtering
**Root Cause:** "moral" missing from METADATA_KEYWORDS set
**Fix:** Add "moral" to METADATA_KEYWORDS
**Status:** ✅ **FIXED AND VERIFIED**

This was Bug #3 discovered during user verification, demonstrating the importance of in-game validation even after binary analysis confirms data presence.
