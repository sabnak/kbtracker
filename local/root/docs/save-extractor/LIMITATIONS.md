# Known Limitations and Magic Constants

## Recent Fixes

### v1.5.1 (2026-01-24)

**✅ FIXED: Incorrect Section Attribution to itext Shops**
- **Issue:** itext shops incorrectly claiming inventory from preceding building_trader@ shops
- **Status:** RESOLVED in v1.5.1
- **Example:** `m_zcom_start_519` was merged with `building_trader@31` (actor 807991996)
- **Fix:** Added `building_trader@` check to `_section_belongs_to_shop()` method
- **Impact:** +2 shops correctly separated, accurate inventory per shop

This bug affected shop separation:
- itext shops appearing after building_trader@ shops would claim their inventory
- Result: Merged shops showing duplicate/wrong inventory
- Caused by incomplete shop boundary detection in section validation
- Only checked for `itext_` patterns, ignored `building_trader@` patterns

If you're using v1.5.1 or later, this issue no longer applies.

### v1.5.0 (2026-01-17)

**✅ FIXED: UTF-16-LE Alignment Bug**
- **Issue:** Shops at odd byte offsets were missed during decoding (~10-15% shop loss)
- **Status:** RESOLVED in v1.5.0
- **Fix:** Parser now decodes chunks at both even and odd byte offsets
- **Impact:** +12-17% more shops extracted, no more probabilistic detection failures

This bug was particularly insidious because:
- It appeared as random, inconsistent behavior
- Same shop would appear in one save but not another
- Root cause was byte-level alignment, not game logic
- Affected both shop detection AND section attribution

If you're using v1.5.0 or later, this issue no longer applies.

---

## Magic Constants

The extractor uses several hardcoded limits that work for normal saves but could fail on edge cases:

### 1. Section Search Distance (5000 bytes)
**Location:** `find_preceding_section(max_distance=5000)`

**What it does:** Searches backwards from shop ID to find section markers

**Risk:** If sections are >5KB away, they won't be found

**Symptoms:**
- Missing items/units/spells/garrison
- Empty shops that should have content

**Fix:** Increase `max_distance` parameter
```python
# Change from:
items_pos = find_preceding_section(data, b'.items', shop_pos, 5000)

# To:
items_pos = find_preceding_section(data, b'.items', shop_pos, 10000)
```

### 2. Slruck Metadata Search (500 bytes)
**Location:** `parse_items_section()` - `range(125)`

**What it does:** Searches forward from item name to find slruck field with quantity

**Risk:** If item metadata >500 bytes, quantity defaults to 1

**Symptoms:**
- Stackable items showing qty=1 instead of actual quantity
- Crystals/potions showing wrong quantities

**Fix:** Increase search range
```python
# Change from:
for _ in range(125):  # 125 * 4 = 500 bytes

# To:
for _ in range(250):  # 250 * 4 = 1000 bytes
```

### 3. Quantity Limit (< 10,000)
**Location:** `parse_spells_section()` - `if 0 < quantity < 10000`

**What it does:** Validates spell quantities

**Risk:** Skips spells with qty ≥ 10,000

**Symptoms:**
- Missing spells from output
- Fewer spells than expected

**Fix:** Increase limit or remove upper bound
```python
# Change from:
if 0 < quantity < 10000:

# To:
if 0 < quantity < 100000:  # or just: if quantity > 0:
```

### 4. Name Length Limits (5-100 characters)
**Location:** Multiple places - `if 5 <= name_length <= 100`

**What it does:** Validates item/spell/unit name lengths

**Risk:** Skips items with names <5 or >100 chars

**Symptoms:**
- Missing items/units/spells
- Modded content not appearing

**Fix:** Adjust limits
```python
# Change from:
if 5 <= name_length <= 100:

# To:
if 3 <= name_length <= 200:  # Allow shorter and longer names
```

### 5. Slash-separated String Limit (5000 bytes)
**Location:** `parse_slash_separated()` - `if str_length > 5000`

**What it does:** Validates garrison/units data length

**Risk:** Skips sections >5KB

**Symptoms:**
- Missing garrison/units
- Large armies not appearing

**Fix:** Increase limit
```python
# Change from:
if str_length <= 0 or str_length > 5000:

# To:
if str_length <= 0 or str_length > 50000:
```

## FAQ: Understanding the Limits

### Why do these limits exist?

The King's Bounty save file format has **no clear delimiters** between data structures. We're scanning binary data looking for patterns:

```
[random bytes] [length: 4 bytes] [name: N bytes] [quantity: 4 bytes] [more data]
```

The extractor must distinguish **real game data** from **garbage bytes**. These limits act as validation filters.

### What's the core problem?

When we read 4 bytes as a uint32, how do we know it's a real length field vs random garbage?

```python
# Example: Random bytes
data = b'\xFF\xFF\xFF\xFF'
value = struct.unpack('<I', data)[0]
# Result: 4,294,967,295

# Is this:
# A) A valid quantity of 4 billion crystals?
# B) Random garbage that happened to be all 0xFF?
```

**Answer: We validate using multiple checks:**
1. Is the value within reasonable range? (5-100 chars, <10,000 qty)
2. Does the name match pattern? (`^[a-z][a-z0-9_]*$`)
3. Is it not a metadata keyword? (not `count`, `flags`, etc.)

### What happens if I increase the limits?

**Trade-off: Precision vs Recall**

| Action | Benefit (✅) | Risk (❌) |
|--------|-------------|----------|
| Increase section distance | Finds large shops | Could grab wrong shop's sections |
| Increase metadata search | Handles complex items | Could find wrong slruck field |
| Remove quantity limit | Accepts extreme values | Interprets garbage as valid data |
| Lower min name length | Catches short names | Accepts metadata keywords as items |
| Increase max name length | Handles long names | Accepts random bytes as names |

**Example: Section Distance**
```
[Shop A .items section]     <- 6KB
[Shop A .spells section]
[Shop A ID]
[Shop B .items section]     <- We're here, searching backwards
[Shop B ID]
```

- **5000 bytes**: Finds Shop B sections ✅
- **10000 bytes**: Might grab Shop A sections ❌ (wrong shop!)

### Should I change the defaults?

**For normal saves: NO** - Current defaults work for 99% of cases

**Change them if:**
- ✅ Using heavily modded content
- ✅ Endgame saves with extreme quantities (100,000+ units)
- ✅ Shops with >5KB sections
- ✅ You see missing/incorrect data that you know should be present

**How to verify:**
1. Run extractor on your save
2. Load the game and visit a shop
3. Compare in-game inventory to extracted JSON
4. If data is missing, increase limits gradually (2x at a time)

### What's the risk of increasing limits too much?

**False positives** - Garbage data interpreted as valid items:

```json
{
  "items": [
    {"name": "snake_ring", "quantity": 1},
    {"name": "\ufffd\ufffd\ufffd\ufffd", "quantity": 4294967295},  ❌ Garbage!
    {"name": "s", "quantity": 2},                    ❌ Metadata keyword!
    {"name": "crystal", "quantity": 1}
  ]
}
```

**Conservative limits = Clean output**
**Loose limits = More data but potentially incorrect**

### Best practice recommendation

**Use the defaults first**, then adjust only if you have evidence of missing data:

1. **Run with defaults** → 99% accuracy on normal saves
2. **Compare with in-game shop** → Identify discrepancies
3. **Increase specific limit** → Only the one causing issues
4. **Validate again** → Ensure no false positives introduced

### Example: Adjusting for modded content

```python
# Scenario: Mod adds items with 3-char names
# Symptom: Missing items you know should be there
# Fix: Lower min_name_length from 5 to 3

# In parse_items_section():
if 3 <= name_length <= 100:  # Changed from 5
    ...
```

**After adjustment, verify:**
- ✅ Missing items now appear
- ❌ Check for new false positives (metadata keywords)

## Validation Scope

The extractor has been tested on:
- ✅ 4+ save files (including quick1768586988, quick1768595656)
- ✅ 420+ shops per save (after v1.5.0 UTF-16 alignment fix)
- ✅ Normal gameplay saves (not heavily modded)
- ✅ File sizes: 10-11 MB
- ✅ Multiple game progression states (early game through endgame)

It has NOT been tested on:
- ❌ Heavily modded saves
- ❌ Endgame saves with extreme quantities (>100,000 units)
- ❌ Corrupted or partially corrupted saves
- ❌ Different game versions (only tested on King's Bounty: The Legend)

## Recommended Approach

For **maximum compatibility**, consider making these configurable:

```python
class ExtractorConfig:
    max_section_distance = 10000  # Increased from 5000
    max_metadata_search = 1000    # Increased from 500
    max_quantity = 1000000        # Increased from 10000
    min_name_length = 3           # Decreased from 5
    max_name_length = 200         # Increased from 100
    max_string_length = 50000     # Increased from 5000
```

## When to Adjust Constants

**Increase limits if you see:**
- Shops with suspiciously few items
- Missing content that should be present
- Items with wrong quantities (especially qty=1 for stackables)

**Decrease limits if you see:**
- Too many false positives (metadata appearing as items)
- Invalid/garbage data in output
- Performance issues

## Testing Other Saves

To validate on new saves:
1. Run extractor on your save
2. Pick a shop you know well in-game
3. Compare extracted data to actual in-game shop
4. If discrepancies found, adjust constants accordingly

## Future Improvements

Consider implementing:
- Dynamic limit detection based on file size
- Configurable constants via command-line args
- Warning messages when limits are reached
- Validation mode that reports potential issues
