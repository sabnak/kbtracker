# Shop Inventory Parser Investigation - 2026-01-05

## Investigation Index

This directory contains a complete forensic analysis of shop inventory parsing bugs in save file `/saves/Darkside/1767631838`.

## Quick Start

**For executive summary**: Read `README.md`
**For complete technical details**: Read `FINAL_REPORT.md`
**For visual explanation**: Run `visual_summary.py`

## Files Overview

### Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Executive summary with key findings | All stakeholders |
| `FINAL_REPORT.md` | Complete technical analysis with code examples | Developers |
| `INDEX.md` | This file - navigation guide | All users |

### Analysis Scripts

All scripts are executable and can be run with: `python3 <script_name>`

| Script | Purpose | Output |
|--------|---------|--------|
| `analyze_shops.py` | Initial section structure analysis | Section positions and unit data |
| `detailed_analysis.py` | Deep dive into section ordering | Step-by-step parser logic trace |
| `verify_parser_bug.py` | Simulates parser bug with actual data | Demonstrates backwards range issue |
| `analyze_spells.py` | Investigates false positive spells | Shows section sharing between shops |
| `find_spell_owner.py` | Identifies actual spell section owner | Proves cross-shop attribution |
| `visual_summary.py` | ASCII diagrams of bugs | Visual explanation of issues |

## Key Findings

### Bug #1: Missing Units (HIGH Severity)

**Shop**: `m_portland_8671`
**Expected**: 4 units (pirat, pirat2, bocman, sea_magess)
**Actual**: 0 units
**Cause**: Parser calculates backwards range when .spells appears before .shopunits

### Bug #2: False Positive Spells (MEDIUM Severity)

**Shops**: `m_portland_6671` and `m_portland_8671`
**Expected**: 0 spells
**Actual**: 2 spells each (spell_advspell_summon_bandit, spell_advspell_summon_human)
**Cause**: Parser searches too far backwards, crossing shop boundaries

## Root Cause

Both bugs stem from incorrect assumptions in `ShopInventoryParser.py`:

1. **Assumption**: Sections appear in fixed order (.garrison -> .items -> .shopunits -> .spells)
   **Reality**: Sections can appear in ANY order

2. **Assumption**: Nearest section marker belongs to current shop
   **Reality**: Parser search range (5000 bytes) crosses shop boundaries

## Recommendations

1. Calculate section boundaries based on actual positions, not assumptions
2. Verify section ownership before parsing (check for intervening shop IDs)
3. Only use sections that come AFTER the current section as end boundaries

See `FINAL_REPORT.md` section "Recommendations for Parser Fixes" for implementation details.

## Investigation Timeline

1. Reproduced issue with parser (`s /saves/Darkside/1767631838`)
2. Created `analyze_shops.py` - discovered section ordering issue
3. Created `detailed_analysis.py` - traced exact parser logic
4. Created `verify_parser_bug.py` - confirmed backwards range bug
5. Created `analyze_spells.py` - discovered section sharing
6. Created `find_spell_owner.py` - identified actual spell owner
7. Created `visual_summary.py` - visualized bugs with ASCII art
8. Documented findings in `README.md` and `FINAL_REPORT.md`

## Evidence Summary

### Binary Evidence

Shop `m_portland_8671` contains units in binary:
```
Position: 56138 to 56237
Content: "pirat/440/pirat2/260/bocman/52/sea_magess/35"
```

Parser uses wrong range:
```
data[56138:51681]  <- Backwards, returns empty
```

Correct range:
```
data[56138:56237]  <- Forward to .temp marker, finds units
```

### Section Attribution Evidence

.spells section at position 51681:
- Belongs to: `m_zcom_1308` (at position 51961)
- Incorrectly parsed by: `m_portland_6671`, `m_portland_8671`
- Distance from m_portland_8671: 4739 bytes (within 5000 byte search range)

## Testing Commands

Run all analysis scripts:
```bash
cd /app
python3 tests/research/save_decompiler/kb_shop_extractor/2026-01-05/analyze_shops.py
python3 tests/research/save_decompiler/kb_shop_extractor/2026-01-05/detailed_analysis.py
python3 tests/research/save_decompiler/kb_shop_extractor/2026-01-05/verify_parser_bug.py
python3 tests/research/save_decompiler/kb_shop_extractor/2026-01-05/analyze_spells.py
python3 tests/research/save_decompiler/kb_shop_extractor/2026-01-05/find_spell_owner.py
python3 tests/research/save_decompiler/kb_shop_extractor/2026-01-05/visual_summary.py
```

Run parser on save file:
```bash
s /saves/Darkside/1767631838
```

## Related Documentation

- Parser source: `/app/src/utils/parsers/save_data/ShopInventoryParser.py`
- Save format docs: `/app/docs/save-extractor/README.md`
- Previous research: `/app/tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/`

## Conclusion

Investigation complete. Root causes identified with binary-level evidence. Parser requires updates to:
1. Handle sections in any order
2. Verify section ownership before parsing
3. Use position-based logic instead of assumption-based logic

Impact: HIGH severity (data loss) + MEDIUM severity (false positives)
