# Shop Inventory Parser Investigation - 2026-01-05

## Executive Summary

Investigation of shop inventory parsing issues in save file `/saves/Darkside/1767631838` revealed two critical bugs in `ShopInventoryParser.py`:

1. **Missing Units Bug (HIGH severity)**: Parser uses backwards/invalid range when sections appear out of expected order, causing 4 visible units to be completely missing from output
2. **False Positive Spells Bug (MEDIUM severity)**: Parser attributes sections to wrong shop by searching too far backwards across shop boundaries

## Problem Overview

### Shop `m_portland_6671`
- Parser output: 2 spells
- Player sees: Empty shop
- Issue: Spells belong to different shop (false positives)

### Shop `m_portland_8671` (CRITICAL)
- Parser output: 2 spells
- Player sees: 4 units (pirat, pirat2, bocman, sea_magess)
- Issue: Parser missing all 4 visible units + showing false positive spells

## Root Causes

### Bug #1: Backwards Range Calculation

**Location:** `ShopInventoryParser.py` lines 397-400

The parser assumes section order: `.garrison -> .items -> .shopunits -> .spells`

But actual order is: `.spells (51681) -> .shopunits (56138) -> shop_id (56420)`

Current code:
```python
next_pos = spells_pos if spells_pos else shop_pos  # Gets 51681
result[units] = self._parse_slash_separated(data, 56138, 51681)  # BACKWARDS!
```

Result: `data[56138:51681]` is empty, `data.find(b"strg", 56138, 51681)` returns -1

**Solution:** Only use sections that come AFTER the current section

### Bug #2: Cross-Shop Section Attribution

Parser searches backwards 5000 bytes from shop ID, which crosses shop boundaries.

Shop `m_portland_8671` at position 56420 finds `.spells` at 51681, but this belongs to shop `m_zcom_1308` at position 51961.

**Solution:** Verify no shop ID exists between section and current shop

## Binary Evidence

### Shop `m_portland_8671` Contains Units

```
.shopunits section: position 56138 to 56237
strg marker at offset 39
Content: "pirat/440/pirat2/260/bocman/52/sea_magess/35"
```

Units ARE in the save file. Parser just uses wrong range to search for them.

### Spells Belong to Different Shop

```
.spells section at 51681
Next shop ID: m_zcom_1308 at ~51961

Both m_portland_6671 and m_portland_8671 find this SAME .spells section
But it belongs to m_zcom_1308, not the portland shops
```

## Recommendations

### Fix #1: Calculate Section Boundaries Correctly

Replace hardcoded order assumptions with position-based logic:

```python
if units_pos:
    # Find next section marker AFTER units_pos
    next_pos = shop_pos
    for section_pos in [spells_pos, temp_pos, items_pos, garrison_pos]:
        if section_pos and units_pos < section_pos < shop_pos:
            next_pos = min(next_pos, section_pos)
    # Now next_pos is guaranteed to be >= units_pos
```

### Fix #2: Verify Section Ownership

Add validation to prevent cross-shop attribution:

```python
def _section_belongs_to_shop(self, data: bytes, section_pos: int, shop_pos: int) -> bool:
    chunk = data[section_pos:shop_pos]
    text = chunk.decode("utf-16-le", errors="ignore")
    # If another shop ID exists between section and shop, section is not ours
    return not re.search(r"itext_[a-z_-]+_\d+", text)
```

### Fix #3: Refactor to Handle Any Section Order

Process sections by actual position, not assumed order. See FINAL_REPORT.md for detailed implementation.

## Investigation Files

Created analysis scripts in `/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-05/`:
- `analyze_shops.py` - Section structure analysis
- `detailed_analysis.py` - Section ordering investigation
- `verify_parser_bug.py` - Parser bug simulation
- `analyze_spells.py` - False positive analysis
- `find_spell_owner.py` - Section ownership verification

See `FINAL_REPORT.md` for complete technical details.

## Conclusion

Parser has fundamental flaw: assumes sections appear in fixed order and nearest section belongs to current shop. Both assumptions are wrong.

Impact:
- HIGH severity: Loses visible game data (4 units missing)
- MEDIUM severity: Adds incorrect data (false positive spells)

Fix requires updating section boundary calculation logic to be position-based instead of assumption-based.
