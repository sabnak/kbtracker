# Bug Report: AtomParser Incompatibility with items.txt Format

## Date
2026-01-01

## Summary
Attempted to replace manual parsing in `KFSItemsParser._parse_items_file()` with `AtomParser` to reduce code complexity and leverage existing tested parser. The integration failed due to structural incompatibilities between the items.txt file format and the atom format that AtomParser was designed to parse.

## Attempted Change
**Goal**: Replace ~90 lines of manual line-by-line parsing logic with `AtomParser.parse()` to:
- Reduce code complexity
- Leverage existing tested parser
- Improve maintainability
- Automatic type conversion and comment handling

**Files affected**:
- `src/utils/parsers/game_data/KFSItemsParser.py` - Replace `_parse_items_file()` and remove `_parse_item_block()`
- `tests/domain/game/utils/conftest.py` - Fixed incorrect imports (unrelated issue)

## Issues Discovered

### Issue 1: Empty Field Values Followed by Block Names

**Problem**: When items.txt has an empty field value immediately followed by a block name on the next line, AtomParser incorrectly tokenizes them as a single key-value pair.

**Example - rage_ring item**:

Raw items.txt structure:
```
rage_ring {
  category=o
  image=heroitem_addon_ring02.png
  price=0
  level=4
  propbits=
  params {}
}
```

**Expected parsing**:
```python
{
    'rage_ring': {
        'propbits': '',  # Empty string
        'params': {}
    }
}
```

**Actual AtomParser output**:
```python
{
    'rage_ring': {
        'propbits': 'params',  # Block name treated as field value!
        'params': {}
    }
}
```

**Root cause**: AtomParser's tokenizer splits on whitespace and special characters (`{}=`), but doesn't preserve line boundaries. The sequence `propbits=` followed by newline and `params {` gets tokenized as `['propbits', '=', 'params', '{', '}']`, causing the parser to interpret `params` as the value for `propbits`.

**Impact**: This caused `InvalidPropbitException` errors when trying to parse 'params', 'setbonus', 'actions', 'mods', etc. as Propbit enum values.

### Issue 2: Top-Level Configuration Blocks

**Problem**: The items.txt file contains top-level configuration blocks that are not items but are parsed as such by AtomParser.

**Examples found**:
- `params` - Global parameters block (list of 400+ param configurations)
- `actions` - Global actions block (list of action handlers)
- `mods` - Modifications block
- `setbonus` - Set bonus configurations
- `atoms`, `use`, `fight`, `filter`, `troops`, `army`, `trap`, `shield` - Various configuration blocks

**AtomParser output**:
```python
{
    'params': [...],      # Should be ignored (global config)
    'actions': [...],     # Should be ignored (global config)
    'snake_belt': {...},  # Valid item
    'rage_ring': {...},   # Valid item
    ...
}
```

**Expected behavior**: Manual parser only extracts item blocks (those starting with item identifiers, not configuration keywords).

**Attempted fix**: Added block name filtering, but this is a workaround for a deeper structural issue.

### Issue 3: Syntax Error - Unexpected End of File

**Problem**: AtomParser raises `AtomSyntaxError: "Unexpected end of file, expected }"` when parsing the full items.txt file.

**Error trace**:
```
src/utils/parsers/atom/AtomParser.py:158: in _parse_block
    raise AtomSyntaxError("Unexpected end of file, expected }")
E   src.utils.parsers.atom.exceptions.AtomSyntaxError: Unexpected end of file, expected }
```

**Analysis**: This suggests brace mismatch or structural differences between items.txt format and the atom format. The items.txt file may have:
- Non-standard nesting patterns
- Empty blocks with different syntax
- Conditional or context-specific parsing rules not handled by AtomParser

**Impact**: Cannot parse the complete items.txt file, blocking the integration entirely.

### Issue 4: Data Quality - Invalid Propbit Values

**Problem**: Multiple items in the test data have invalid `propbits` values that happen to be block names.

**Items affected**:
- `rage_ring`: `propbits='params'`
- Other items likely affected: Items with empty propbits followed by various block names

**Is this a bug?**: Unclear if this is:
1. Bad test data (items.txt file has malformed entries)
2. Intended behavior (empty propbits should be skipped)
3. Parser artifact (manual parser handles this differently)

## Test Results

**Before changes**: All 11 tests passing
**After integration**: All 11 tests failing with various errors:
- `InvalidPropbitException: Invalid propbit value 'params'`
- `InvalidPropbitException: Invalid propbit value 'setbonus'`
- `AtomSyntaxError: Unexpected end of file, expected }`

## Root Cause Analysis

### Format Differences

**Atom format (`.atom` files)**:
- Strict hierarchical structure with balanced braces
- All fields have explicit values
- Used for: 3D models, effects, spells metadata
- Clean, well-formed syntax

**Items.txt format**:
- Hybrid format mixing items and global configuration blocks
- Allows empty field values (e.g., `propbits=` with no value)
- Contains include directives at the top (e.g., `==medals.txt`)
- May have looser brace balancing rules
- Legacy format with accumulated quirks

### AtomParser Design Limitations

AtomParser was designed for strict `.atom` files and makes these assumptions:
1. All blocks are valid data structures (no distinction between items and config)
2. Field values are always present (no empty values)
3. Tokens can be safely split on whitespace without line context
4. Brace nesting is strictly balanced

These assumptions don't hold for items.txt format.

## Attempted Workarounds

### Workaround 1: Filter Block Names
```python
block_names = {
    'params', 'actions', 'mods', 'atoms', 'use', 'fight',
    'filter', 'troops', 'setbonus', 'army', 'trap', 'shield'
}

# Skip known configuration blocks
if kb_id in block_names:
    continue

# Skip if value is a block name (parser artifact)
if field == 'propbits' and value in block_names:
    continue
```

**Result**: Partially worked, but hit syntax errors before completing parse.

### Workaround 2: Pre-process Empty Values
Could normalize empty values before parsing:
```python
content = re.sub(r'(\w+)=\s*\n', r'\1=""\n', content)
```

**Not attempted**: Would require extensive testing and might break other parsing.

## Recommendations

### Option 1: Keep Manual Parsing (Recommended)
**Pros**:
- Already works correctly with items.txt format
- Handles all edge cases (empty values, config blocks, etc.)
- Proven through existing test suite
- No risk of regression

**Cons**:
- ~90 lines of manual parsing code
- Duplicates some logic that AtomParser provides

**Verdict**: Manual parsing exists for a reason - the format has quirks that require custom handling.

### Option 2: Extend AtomParser
Create `ItemsTxtParser` that extends `AtomParser` with:
- Line-aware tokenization (preserve empty values)
- Item vs. config block detection
- Relaxed brace matching rules

**Pros**:
- Could reuse some AtomParser infrastructure
- More maintainable long-term

**Cons**:
- Significant development effort
- Risk of introducing bugs
- May not be worth it for a single use case

### Option 3: Fix Test Data
If items with `propbits='params'` are actually malformed, fix the source data.

**Investigation needed**:
- Check if `rage_ring` should have empty propbits or a valid value
- Verify against production game files
- Determine if this is a test data issue or format quirk

### Option 4: Create Dedicated ItemsTxt Parser
Build a new parser specifically for items.txt that:
- Understands the hybrid item/config structure
- Handles empty values correctly
- Maintains compatibility with existing format quirks

**Pros**:
- Clean separation of concerns
- Can handle format-specific rules

**Cons**:
- Most complex option
- Duplicates effort

## Conclusion

The items.txt format is **not compatible** with AtomParser due to fundamental structural differences. The manual parsing approach in `KFSItemsParser._parse_items_file()` should be retained as it correctly handles the format's quirks.

**Recommended action**: Close this integration attempt and keep existing implementation.

## Additional Notes

### Files for Reference
- Test file: `tests/game_files/sessions/*/ses.kfs/items.txt`
- AtomParser: `src/utils/parsers/atom/AtomParser.py`
- Current implementation: `src/utils/parsers/game_data/KFSItemsParser.py` (lines 119-207)

### Related Issues
- Fixed unrelated bug in `tests/domain/game/utils/conftest.py`: Imports were using package names instead of class names for `KFSExtractor` and `KFSLocationsAndShopsParser` (lines 6, 9)

## Investigation Commands Used

```bash
# Debug AtomParser output
docker exec kbtracker_app bash -c 'cd /app && python debug_parser.py'

# Find items with problematic propbits
docker exec kbtracker_app bash -c 'cd /app && python debug_parser4.py'

# Extract raw item structure
docker exec kbtracker_app bash -c 'cd /app && python debug_raw_rage_ring.py'

# Run tests
docker exec kbtracker_app bash -c 'cd /app && pytest tests/domain/game/utils/test_KFSItemsParser.py -v'
```
