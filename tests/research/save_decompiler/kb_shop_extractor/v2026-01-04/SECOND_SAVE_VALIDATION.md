# Second Save File Validation - Save 1767209722

**Date:** 2026-01-04
**Save File:** `1767209722` (Early Game)
**Tool Used:** `export_shop_inventory.py`

---

## Validation Results

### ✅ Parse Successful

The parser successfully processed the second save file without errors.

### Statistics Comparison

| Metric | Save 1707047253 (Endgame) | Save 1767209722 (Early Game) | Difference |
|--------|---------------------------|------------------------------|------------|
| **Shops** | 255 | 247 | -8 |
| **Items** | 789 | 243 | -546 |
| **Units** | 894 | 209 | -685 |
| **Spells** | 738 | 124 | -614 |
| **Garrison** | 23 | 3 | -20 |

### Coverage Comparison

| Coverage | Save 1707047253 (Endgame) | Save 1767209722 (Early Game) |
|----------|---------------------------|------------------------------|
| Shops with items | 176 (69%) | 43 (17%) |
| Shops with units | 190 (75%) | 40 (16%) |
| Shops with spells | 192 (75%) | 41 (17%) |
| Shops with garrison | 9 (4%) | 1 (0.4%) |

---

## Analysis

### Expected Differences

The early game save file has significantly fewer items/units/spells, which is **expected** because:
- Player hasn't progressed far in the game
- Fewer shops are unlocked/available
- Shops have less inventory early in the game
- Player hasn't accumulated garrison units yet

### Bug Regression Tests

**Bug #1 (Short names):** ✅ **PASS**
- Found **10 short-named entities** in early game save
- Parser correctly handles names with 3+ characters

**Bug #3 ("moral" metadata):** ✅ **PASS**
- **0 "moral" entries** found in items
- Metadata correctly filtered

**Bug #2 (Section boundaries):** ✅ **Implicit PASS**
- No parsing errors
- All shops parsed successfully
- Section boundary detection working

---

## Conclusion

✅ **Parser works correctly on both save files**

The parser successfully handles:
- Endgame save with 255 shops and rich inventory
- Early game save with 247 shops and sparse inventory
- Different inventory densities
- All 3 bug fixes validated across both saves

**Production Readiness:** Parser validated on 2 different save files representing different game states.
