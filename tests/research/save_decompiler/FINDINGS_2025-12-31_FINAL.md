# Final Save Decompiler Findings - December 31, 2025

## Shop Data Structure - CONFIRMED

Each shop in the save file has:
1. **Items** (in `.items` section)
2. **Spells** (in `.spells` section)
3. **Units** (in `.shopunits` section)

All three types include **quantities** for each product.

## Section Layout Pattern

Sections appear **BEFORE** the shop ID in this order:

```
[.items section]     ← Items with quantities
[.shopunits section] ← Units with quantities
[.spells section]    ← Spells with quantities
[Shop ID UTF-16 LE]  ← "itext_m_<location>_<number>"
```

### Example: Shop `itext_m_zcom_1422`

```
Offset    Distance    Content
627891    -2983      .items section (contains 9 items)
629039    -1835      .shopunits section (contains units)
629793    -1081      .spells section (contains 32 spells)
630874      0        Shop ID: "itext_m_zcom_1422"
```

## Critical Discovery: Count Headers Are WRONG

**The count field in section headers is UNRELIABLE!**

- Items section header: says 9, actually has 10+ items
- Spells section header: says 2, actually has 32 spells
- Units section header: varies

**Solution:** Scan the ENTIRE section from marker to shop ID, not just `count` entries.

## Section Extent

Each section extends from its marker **all the way to the shop ID**:

```
Section start: [marker position]
Section end:   [shop ID position]
Scan range:    entire gap between marker and shop ID
```

## Product Entry Format

Each product (item/spell/unit) has:

```
4 bytes: name_length (uint32, little-endian)
N bytes: name (ASCII, pattern: ^[a-z][a-z0-9_]*$)
4 bytes: quantity (uint32, little-endian)
... variable metadata ...
[next entry or end of section]
```

### Example

```hex
0D 00 00 00                    # Length: 13
73 70 65 6C 6C 5F 68 65 61    # "spell_healing"
6C 69 6E 67
06 00 00 00                    # Quantity: 6
... metadata ...
```

## Parsing Algorithm

```python
def parse_section(data, section_start, shop_id_pos):
    products = {}

    # Scan entire section
    pos = section_start
    while pos < shop_id_pos - 20:
        # Try to read entry at current position
        name_length = read_uint32(data, pos)

        if 5 <= name_length <= 100:  # Reasonable length
            name = try_decode_ascii(data[pos+4 : pos+4+name_length])

            if is_valid_id(name):
                quantity = read_uint32(data, pos+4+name_length)

                if 0 < quantity < 10000:  # Reasonable quantity
                    products[name] = max(products.get(name, 0), quantity)
                    pos += 4 + name_length + 4
                    continue

        pos += 1  # Move forward 1 byte

    return products
```

## Validation Rules

### Valid Item/Spell/Unit ID

```python
pattern = r'^[a-z][a-z0-9_]*$'
```

- Must start with lowercase letter
- Can contain: lowercase letters, digits, underscores
- Cannot contain: `/`, `,`, uppercase letters

### Invalid Metadata Strings

These appear in `.items` sections but are NOT items:

- `upgrade/item1,item2/rndid/123`
- `use/N/item_add/scroll/scroll/spell/rndid/123`
- `item_count/N/victory/N/rndid/123`
- `map/N/image/picture/rndid/123`

**Filter these out** during parsing.

## Test Case: Shop `itext_m_zcom_1422`

### Items (9 total)
```
addon4_dwarf_simple_belt x4
addon4_elf_bird_armor x4
addon4_elf_botanic_book x4
addon4_elf_fairy_amulet x4
addon4_human_life_cup x4
exorcist_necklace x4
fire_master_braces x4
moon_sword x4
tournament_helm x4  ← Previously missing!
```

### Spells (32 total) ✅
```
spell_blind x1
spell_chaos_coagulate x2
spell_cold_grasp x2
spell_defenseless x1
spell_demonologist x1
spell_desintegration x4
spell_dispell x4
spell_dragon_arrow x2
spell_empathy x4
spell_fire_breath x3
spell_fire_shield x1
spell_ghost_sword x2
spell_gold_rush x4
spell_healing x6
spell_holy_rain x1
spell_horde_totem x1
spell_kamikaze x2
spell_life_stealer x2
spell_lull x7
spell_magic_source x2
spell_mine_field x2
spell_pain_mirror x2
spell_plague x1
spell_raise_dead x3
spell_revival x2
spell_scare x3
spell_shifted_time x2
spell_slow x1
spell_undertaker x3
spell_wasp_swarm x1
spell_weakness x1
spell_winter_dance x1
```

**All user-verified spells found with correct quantities!** ✅

## Parser Implementation

### File: `parse_complete_shop_final.py`

Features:
- ✅ Scans entire section from marker to shop ID
- ✅ Ignores unreliable count headers
- ✅ Validates item/spell/unit IDs
- ✅ Filters out metadata strings
- ✅ Extracts quantities
- ✅ Handles all three product types

## Next Steps

1. ✅ Understand shop structure (3 product types)
2. ✅ Identify section layout pattern
3. ✅ Discover count headers are wrong
4. ✅ Fix parser to scan entire sections
5. ✅ Verify with user data (32 spells confirmed!)
6. ⏳ Create final parser for ALL shops
7. ⏳ Generate complete JSON output
8. ⏳ Integrate into main application

## Success Metrics

**Test Shop: `itext_m_zcom_1422`**
- ✅ Items: 9/9 found (including `tournament_helm`)
- ✅ Spells: 32/32 found (all user-verified spells match!)
- ⏳ Units: To be tested

**Status:** Parser working correctly! ✅
