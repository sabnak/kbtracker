# Bug Root Causes - Save File Parser

**Date:** 2026-01-04
**Investigation Method:** Binary analysis with Construct library
**Tool:** Interactive shop explorer + hex dumps

---

## Summary

All reported bugs traced to **2 root causes** in `ShopInventoryParser.py`:

1. **Minimum length validation** (5 characters) filters out valid short-named entities
2. **Missing section boundary detection** for `.temp` marker causes parsing beyond intended sections

---

## Bug 1: Missing Entities (Shop `atrixus_late_708`)

### Reported Issues
- Missing item: `trap`
- Missing units: `imp`, `imp2`

### Investigation Results

**Binary Data Analysis:**
```
Items section contains:
  - Length: 4, Name: "trap" ✓ Present in binary

Units section contains:
  - String: "imp2/2250/imp/810/cerberus/490" ✓ All present in binary
```

**Current Parser Output:**
```
Items: 4 items (trap missing)
Units: 1 unit (only cerberus, imp and imp2 missing)
```

### Root Cause

**File:** `src/utils/parsers/save_data/ShopInventoryParser.py`
**Line:** 397
**Method:** `_is_valid_id()`

```python
def _is_valid_id(self, item_id: str) -> bool:
	if not item_id or item_id in self.METADATA_KEYWORDS or len(item_id) < 5:  # ← HERE
		return False
	return bool(re.match(r'^[a-z][a-z0-9_]*$', item_id))
```

**The validation requires `len(item_id) >= 5`**, which rejects:
- `"trap"` (length 4) from items section
- `"imp"` (length 3) from units section
- `"imp2"` (length 4) from units section

**Also affects:**
- Line 246 in `_parse_items_section()` - same validation for item names
- Line 319 in `_parse_spells_section()` - same validation for spell names

### Evidence

**Binary proof that entities exist:**
```bash
# Item "trap" found in binary
Position 601 (absolute: 600207):
  Length prefix: 04 00 00 00  (4 bytes)
  Name: 74 72 61 70  ("trap")

# Units found in binary
String: "imp2/2250/imp/810/cerberus/490"
  - imp2: 4 characters
  - imp: 3 characters
  - cerberus: 8 characters ✓ (only this one passes validation)
```

### Impact

Any entity with name length < 5 characters is silently filtered out, including:
- Items with short names (e.g., "trap", "bow", "axe")
- Units with short names (e.g., "imp", "orc", "elf")
- Spells with short names (unlikely, but possible)

---

## Bug 2: Invalid Spell Entries (Shop `atrixus_10`)

### Reported Issues
Invalid entries in spells section:
- `adisabled` ❌ (not a spell)
- `book_times` ❌ (not a spell)
- `dragondor` ❌ (not a spell)
- `territory` ❌ (not a spell)

### Investigation Results

**Binary Data Analysis:**
```
Spells section structure:
  Offset 0x000: ".spells" marker
  Offset 0x060: "spell_advspell_summon_dwarf" ✓ Valid spell
  Offset 0x080: "spell_advspell_summon_mech" ✓ Valid spell
  Offset 0x0C7: ".temp" marker ← SECTION BOUNDARY
  Offset 0x365: "adisabled" ❌ (in .temp section, not .spells!)
  Offset 0x480: "book_times" ❌ (in .temp section)
  Offset 0x846: "territory" ❌ (in .temp section)
  Offset 0x968: "dragondor" ❌ (in .temp section)
```

**Current Parser Output:**
```
Spells (6):
  - adisabled x3 ❌
  - book_times x2 ❌
  - dragondor x2 ❌
  - spell_advspell_summon_dwarf x1 ✓
  - spell_advspell_summon_mech x1 ✓
  - territory x2 ❌
```

### Root Cause

**File:** `src/utils/parsers/save_data/ShopInventoryParser.py`
**Lines:** 290-344
**Method:** `_parse_spells_section()`

The parser uses this logic to determine section boundaries:
```python
def _parse_shop(self, data: bytes, shop_id: str, shop_pos: int) -> dict:
	# Find sections
	garrison_pos = self._find_preceding_section(data, b'.garrison', shop_pos, 5000)
	items_pos = self._find_preceding_section(data, b'.items', shop_pos, 5000)
	units_pos = self._find_preceding_section(data, b'.shopunits', shop_pos, 5000)
	spells_pos = self._find_preceding_section(data, b'.spells', shop_pos, 5000)

	# Parse spells: from spells_pos to shop_pos
	if spells_pos:
		result['spells'] = self._parse_spells_section(data, spells_pos, shop_pos)  # ← HERE
```

**The parser assumes spells section ends at `shop_pos` (shop ID position)**, but there can be intermediate sections like `.temp` between `.spells` and the shop ID!

**Known section markers NOT being detected:**
- `.temp` - found in shop `atrixus_10`
- Potentially others (`.misc`, `.data`, etc.)

### Evidence

**Hex dump showing `.temp` marker:**
```
Offset 0x0C0 in .spells section:
00 00 00 05 00 00 00 2E  74 65 6D 70 02 00 00 00
                     ^^^^^^^^^
                     ".temp" marker

This marker appears AFTER the last valid spell and BEFORE the invalid entries.
```

**Parser behavior:**
1. Finds `.spells` at offset 0x000
2. Scans until `shop_pos` (shop ID)
3. **Does NOT recognize `.temp` as a boundary**
4. Continues parsing data from `.temp` section as if it were spells
5. Returns invalid entries that match the pattern

### Impact

Any shop with intermediate sections (`.temp`, etc.) between `.spells` and shop ID will have:
- Invalid entries included in spells list
- Data from other sections incorrectly parsed as spells
- Contaminated shop inventory data

---

## Fixes Required

### Fix 1: Reduce Minimum Length Validation

**File:** `src/utils/parsers/save_data/ShopInventoryParser.py`
**Line:** 397 (and also lines 246, 319)

**Current:**
```python
if not item_id or item_id in self.METADATA_KEYWORDS or len(item_id) < 5:
	return False
```

**Proposed:**
```python
if not item_id or item_id in self.METADATA_KEYWORDS or len(item_id) < 3:
	return False
```

**Rationale:**
- Minimum 3 characters allows "imp", "bow", "axe", etc.
- Still filters out very short noise (1-2 characters)
- Matches actual game data (confirmed "imp" exists in-game)

**Alternative:** Remove length check entirely if all validation should be pattern-based.

### Fix 2: Detect Intermediate Section Markers

**File:** `src/utils/parsers/save_data/ShopInventoryParser.py`
**Method:** `_parse_spells_section()` (and similar methods)

**Current approach:**
```python
# Scans from spells_pos to shop_pos
while pos < search_end - 20:  # search_end = shop_pos
	# ... parse entries
```

**Proposed approach:**
```python
# Define known section markers
SECTION_MARKERS = {b'.items', b'.spells', b'.shopunits', b'.garrison', b'.temp'}

# Find actual section end
def _find_section_end(self, data: bytes, section_start: int, max_end: int) -> int:
	"""Find where section actually ends by looking for next marker"""
	search_area = data[section_start:max_end]

	earliest_marker_pos = max_end
	for marker in SECTION_MARKERS:
		pos = search_area.find(marker, 1)  # Skip first occurrence (current marker)
		if pos != -1:
			earliest_marker_pos = min(earliest_marker_pos, section_start + pos)

	return earliest_marker_pos

# Use in parsing
actual_end = self._find_section_end(data, spells_pos, shop_pos)
result['spells'] = self._parse_spells_section(data, spells_pos, actual_end)
```

**Rationale:**
- Properly detects section boundaries
- Prevents parsing beyond intended section
- Handles intermediate sections like `.temp`

---

## Testing Plan

### Test Case 1: Short Names
**Shop:** `atrixus_late_708`
**Expected after fix:**
- Items should include `trap`
- Units should include `imp` (x810) and `imp2` (x2250)

### Test Case 2: Section Boundaries
**Shop:** `atrixus_10`
**Expected after fix:**
- Spells should only include entries starting with `spell_`
- Should NOT include: `adisabled`, `book_times`, `dragondor`, `territory`
- Should include: `spell_advspell_summon_dwarf`, `spell_advspell_summon_mech`

### Full Regression Test
- Run parser on both save files (1707047253, 1767209722)
- Compare total counts before/after
- Verify no valid entities are lost
- Verify all invalid entries are removed

---

## Conclusion

Both bugs stem from **incomplete validation logic**:
1. Overly restrictive length validation (removes valid short names)
2. Missing section boundary detection (includes invalid data from adjacent sections)

Fixes are straightforward and localized to `ShopInventoryParser.py`. No changes to binary format understanding required.

**Investigation successful!** ✅
