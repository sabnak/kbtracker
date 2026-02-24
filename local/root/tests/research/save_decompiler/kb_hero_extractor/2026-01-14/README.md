# Hero Name Extractor Research - 2026-01-14

## Objective

Investigate the `info` file structure to extract hero names more reliably than the current `data` file pattern matching approach.

## Background

**Current Implementation:**
- `HeroSaveParser` scans the `data` file for UTF-16LE Cyrillic strings
- Uses pattern matching (`byte2 == 0x04`) and keyword filtering
- **Bug**: For single-name heroes, captures item/unit names as second name

**Discovery:**
- Save files contain both `data` and `info` files
- `info` file has structured field names: `name`, `level`, `rank`, `type`, `leadership`, `heraldic`
- This could provide a more reliable extraction method

## Research Goal

Determine if we should:
1. **Switch to info file** - if it provides reliable structured access to hero names
2. **Keep data file + proximity** - if info file is not reliable or too complex

## Test Cases

| Save File | Hero Names | Expected Result |
|-----------|------------|-----------------|
| `orcs_endgame.sav` | "Зачарованная" | Single name, second_name="" |
| `orcs_startgame.sav` | "Справедливая" | Single name (no inventory yet) |
| `red_sands_Quicksave1.sav` | "Отважная" | Single name |
| `quick1768258578` | "Даэрт" + "де Мортон" | Two names |
| `1707047253` | "Неолина" + "Очаровательная" | Two names |

## Phase 1: Format Analysis

**Tasks:**
- Extract raw info files from all test saves
- Find all occurrences of `name` field
- Analyze byte structure around `name` field
- Determine encoding (UTF-8, UTF-16LE, or other)
- Identify length-prefix or delimiter patterns

**Output:** `01_format_analysis.md`

## Phase 2: Parser Prototype

**Tasks:**
- Implement info file parser
- Extract hero name(s) from all test saves
- Compare with current parser results
- Handle edge cases

**Output:** `02_parser_prototype.py`

## Phase 3: Validation

**Tasks:**
- Test across different save files
- Verify campaign ID stability
- Compare approaches (info vs data+proximity)

**Output:** `03_validation.md`

## Phase 4: Decision

**Tasks:**
- Document pros/cons
- Make recommendation
- Update implementation plan if needed

**Output:** `04_decision.md`

## Progress

- [ ] Phase 1: Format analysis
- [ ] Phase 2: Parser prototype
- [ ] Phase 3: Validation
- [ ] Phase 4: Decision

## Next Steps

1. Extract info files from all test saves to `extracted_samples/`
2. Analyze format and document in `01_format_analysis.md`
3. Build parser prototype
