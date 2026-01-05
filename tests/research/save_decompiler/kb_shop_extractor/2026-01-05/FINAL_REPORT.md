# Shop Inventory Parser Investigation - 2026-01-05

## Problem Statement

Investigation of shop inventory parsing issues in save file `/saves/Darkside/1767631838`.

### Shop 1: `m_portland_6671`
- **Parser Output**: 2 spells (`spell_advspell_summon_bandit` x1, `spell_advspell_summon_human` x1)
- **Player Observation**: Completely empty inventory (no garrison, items, units, or spells)
- **Issue Type**: Parser is finding FALSE POSITIVES from another shop

### Shop 2: `m_portland_8671` - CRITICAL BUG
- **Parser Output**: 2 spells (`spell_advspell_summon_bandit` x1, `spell_advspell_summon_human` x1)
- **Player Observation**: 4 units (pirat, pirat2, bocman, sea_magess) - NO spells
- **Issue Type**: Parser is completely missing 4 visible units AND finding false positive spells

## Investigation Steps

1. Created research directory: `/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-05/`
2. Reviewed documentation: `/docs/save-extractor/README.md`
3. Reviewed previous research: `/tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/BUG_ROOT_CAUSES.md`
4. Ran parser on save file to reproduce issue
5. Created analysis scripts to examine binary structure
6. Identified root cause of missing units
7. Identified root cause of false positive spells

## Root Cause Analysis

### Bug #1: Missing Units in Shop `m_portland_8671`

**Location:** `ShopInventoryParser.py` lines 397-400

**The Problem:**

The parser assumes sections appear in this order:
```
.garrison -> .items -> .shopunits -> .spells -> shop_id
```

But in this save file, the actual order is:
```
.spells (pos 51681) -> .shopunits (pos 56138) -> .temp (pos 56237) -> shop_id (pos 56420)
```

**Current Parser Logic:**
```python
if units_pos:
    next_pos = spells_pos if spells_pos else shop_pos  # Line 398
    actual_end = self._find_section_end(data, units_pos, next_pos)
    result[units] = self._parse_slash_separated(data, units_pos, actual_end)
```

**What Happens:**
1. `units_pos = 56138` (.shopunits position)
2. `spells_pos = 51681` (.spells position)
3. `next_pos = 51681` (spells_pos, because it exists)
4. Parser calls `_find_section_end(data, 56138, 51681)`
5. Search area = `data[56138:51681]` = **EMPTY** (backwards range!)
6. `actual_end = 51681` (no markers found, returns next_pos)
7. Parser calls `_parse_slash_separated(data, 56138, 51681)`
8. `data.find(b"strg", 56138, 51681)` returns `-1` (backwards range!)
9. Parser returns `[]` (empty list)

**Binary Evidence:**

The .shopunits section DOES contain the units:
```
Position: 56138 to 56237 (99 bytes)
strg marker at offset 39
Content: "pirat/440/pirat2/260/bocman/52/sea_magess/35"

Units found:
  - pirat: 440
  - pirat2: 260
  - bocman: 52
  - sea_magess: 35
```

**Correct Range:**

Parser should use: `data[56138:56237]` (shopunits to .temp)
- This is the correct end boundary (.temp marker)
- With this range, `data.find(b"strg", 56138, 56237)` returns `56177`
- Units are successfully parsed

### Bug #2: False Positive Spells in Both Shops

**The Problem:**

Both shops `m_portland_6671` and `m_portland_8671` reference the SAME .spells section at position 51681.

**Section Analysis:**

```
Shop m_portland_6671:
  .spells at 51681
  .temp at 55612
  Shop ID at 55866

Shop m_portland_8671:
  .spells at 51681  <- SAME position!
  .shopunits at 56138
  .temp at 56237
  Shop ID at 56420
```

**Root Cause:**

The .spells section at position 51681 belongs to a DIFFERENT shop:
- Shop `m_zcom_1308` (found at position ~51961, immediately after the .spells section)

**Why This Happens:**

The parser searches BACKWARDS from the shop ID to find section markers:
```python
spells_pos = self._find_preceding_section(data, b".spells", shop_pos, 5000)
```

For both portland shops:
1. Searches backwards 5000 bytes from shop position
2. Finds the .spells section at 51681
3. Assumes it belongs to the current shop
4. Parses spells that actually belong to `m_zcom_1308`

**Evidence:**

The spells ARE valid entries in the binary:
```
spell_advspell_summon_bandit:
  - Position: 51681 + 94
  - Length prefix: 28 (valid)
  - Quantity: 1 (valid)

spell_advspell_summon_human:
  - Position: 51681 + 130
  - Length prefix: 27 (valid)
  - Quantity: 1 (valid)
```

But these spells belong to shop `m_zcom_1308`, not the portland shops!

## Detailed Findings

### Section Structure for Shop `m_portland_8671`

```
Position  Section       Notes
--------  -----------   -----
51681     .spells       Belongs to m_zcom_1308 (WRONG shop!)
51961     [shop_id]     m_zcom_1308
...
56138     .shopunits    Belongs to m_portland_8671 (CORRECT)
56237     .temp         Section boundary
56420     [shop_id]     m_portland_8671
```

### Parser Assumptions vs Reality

| Parser Assumption | Reality | Result |
|------------------|---------|--------|
| Sections ordered: .garrison, .items, .shopunits, .spells | Sections can be in ANY order | Parser uses wrong section boundaries |
| .spells comes AFTER .shopunits | .spells can come BEFORE .shopunits | Backwards range causes empty parsing |
| Nearest .spells section belongs to this shop | .spells may belong to a previous shop | False positive spells from wrong shop |
| All 4 sections exist for each shop | Shops can have only some sections | Parser should handle missing sections |

### Why Shop `m_portland_6671` Shows Spells But Player Sees Empty

Shop `m_portland_6671` has NO sections of its own:
- No .garrison section
- No .items section
- No .shopunits section
- No .spells section

The parser finds the .spells section at 51681, which belongs to `m_zcom_1308`.
The game correctly shows this shop as empty because there are no section markers between the previous shop and this shop ID.

## Recommendations for Parser Fixes

### Fix #1: Correct Section Boundary Calculation

**File:** `ShopInventoryParser.py` lines 397-400

**Current Code:**
```python
if units_pos:
    next_pos = spells_pos if spells_pos else shop_pos
    actual_end = self._find_section_end(data, units_pos, next_pos)
    result[units] = self._parse_slash_separated(data, units_pos, actual_end)
```

**Proposed Fix:**
```python
if units_pos:
    # Find next section marker AFTER units_pos
    next_pos = shop_pos  # Default to shop ID

    # Only consider sections that come AFTER units_pos
    for section_pos in [spells_pos, temp_pos, items_pos, garrison_pos]:
        if section_pos and units_pos < section_pos < shop_pos:
            next_pos = min(next_pos, section_pos)

    actual_end = self._find_section_end(data, units_pos, next_pos)
    result[units] = self._parse_slash_separated(data, units_pos, actual_end)
```

**Similar fixes needed for:**
- Line 393-395 (items section parsing)
- Line 402-404 (spells section parsing)

### Fix #2: Prevent Cross-Shop Section Attribution

**Problem:** Parser searches backwards up to 5000 bytes, which can cross shop boundaries.

**Options:**

**Option A: Reduce search distance**
- Change `max_distance` from 5000 to 500-1000 bytes
- Pros: Simple fix
- Cons: May miss sections for shops with large sections

**Option B: Verify section ownership**
- After finding a section, verify there is no shop ID between the section and current shop
- Pros: Accurate section attribution
- Cons: More complex logic

**Option C: Parse shops in order**
- Process all shops in order by position
- Track which sections have been claimed
- Pros: Most accurate
- Cons: Requires refactoring

**Recommended:** Option B (verify section ownership)

```python
def _section_belongs_to_shop(self, data: bytes, section_pos: int, shop_pos: int) -> bool:
    """
    Verify that no other shop ID exists between section and shop

    :param data: Save file data
    :param section_pos: Section position
    :param shop_pos: Shop ID position
    :return: True if section belongs to this shop
    """
    # Search for shop ID pattern between section and current shop
    chunk = data[section_pos:shop_pos]

    # Look for "itext_" pattern in UTF-16 LE
    import re
    try:
        text = chunk.decode("utf-16-le", errors="ignore")
        # If we find another shop ID, this section does not belong to us
        if re.search(r"itext_[a-z_-]+_\d+", text):
            return False
    except:
        pass

    return True
```

### Fix #3: Handle Section Order Independence

**Problem:** Parser assumes specific section ordering.

**Solution:** Calculate section boundaries based on actual positions, not assumptions.

```python
def _parse_shop(self, data: bytes, shop_id: str, shop_pos: int) -> dict:
    # Find all sections
    sections = {}
    for marker in [b".garrison", b".items", b".shopunits", b".spells"]:
        pos = self._find_preceding_section(data, marker, shop_pos, 5000)
        if pos and self._section_belongs_to_shop(data, pos, shop_pos):
            sections[marker] = pos

    # Sort sections by position
    sorted_sections = sorted(sections.items(), key=lambda x: x[1])

    # Parse each section with correct boundaries
    result = {
        "shop_id": shop_id,
        "garrison": [],
        "items": [],
        "units": [],
        "spells": []
    }

    for i, (marker, section_pos) in enumerate(sorted_sections):
        # Find next boundary (next section or shop ID)
        if i + 1 < len(sorted_sections):
            next_boundary = sorted_sections[i + 1][1]
        else:
            next_boundary = shop_pos

        actual_end = self._find_section_end(data, section_pos, next_boundary)

        # Parse based on section type
        if marker == b".garrison":
            # Find end (next section after garrison)
            ...
        elif marker == b".items":
            result["items"] = self._parse_items_section(data, section_pos, actual_end)
        elif marker == b".shopunits":
            result["units"] = self._parse_slash_separated(data, section_pos, actual_end)
        elif marker == b".spells":
            result["spells"] = self._parse_spells_section(data, section_pos, actual_end)

    return result
```

## Summary

### Critical Bugs Found

1. **Missing Units Bug**: Parser uses backwards range when .spells comes before .shopunits
   - Impact: 4 visible units completely missing from output
   - Severity: HIGH - loses actual game data

2. **False Positive Spells Bug**: Parser attributes sections to wrong shop
   - Impact: Shows spells that do not belong to the shop
   - Severity: MEDIUM - adds incorrect data

### Files Analyzed

- `/saves/Darkside/1767631838/data` (save file)
- `/app/src/utils/parsers/save_data/ShopInventoryParser.py` (parser)
- `/tmp/save_export/1767631838.json` (parser output)

### Scripts Created

- `analyze_shops.py` - Initial section analysis
- `detailed_analysis.py` - Section ordering investigation
- `verify_parser_bug.py` - Parser bug simulation
- `analyze_spells.py` - False positive spell analysis
- `find_spell_owner.py` - Spell section ownership verification

### Evidence Files

All scripts and findings located in:
`/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-05/`

## Conclusion

The ShopInventoryParser has a fundamental flaw in its section boundary calculation logic. It assumes sections appear in a specific order and that the nearest section belongs to the current shop. Both assumptions are incorrect.

The parser must be updated to:
1. Calculate section boundaries based on actual positions, not assumed order
2. Verify section ownership before attributing data to a shop
3. Handle cases where sections appear in any order

The missing units in shop `m_portland_8671` demonstrate data loss (HIGH severity). The false positive spells demonstrate incorrect data attribution (MEDIUM severity). Both issues stem from the same root cause: incorrect section boundary logic.
