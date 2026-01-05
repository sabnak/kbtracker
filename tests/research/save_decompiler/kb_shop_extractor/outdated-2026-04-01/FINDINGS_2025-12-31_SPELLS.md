# Spell and Unit Parsing Investigation - December 31, 2025

## New Discovery: Shops Have Three Product Types

Each shop sells:
1. **Items** - stored in `.items` sections (with quantities)
2. **Spells** - stored in `.spells` sections (with quantities)
3. **Units** - stored in `.shopunits` sections (with quantities)

All three types can stack (quantity > 1).

## Data Structure

Each product entry has:
```
4 bytes: name_length
N bytes: name (ASCII, lowercase, pattern: ^[a-z][a-z0-9_]*$)
4 bytes: quantity (uint32, little-endian)
... metadata ...
```

Example from hex dump:
```
1C 00 00 00                              # Length: 28
73 70 65 6C 6C 5F 61 64 76 73 70 65     # "spell_advspell_summon_viking"
6C 6C 5F 73 75 6D 6D 6F 6E 5F 76 69
6B 69 6E 67
01 00 00 00                              # Quantity: 1
... metadata ...
```

## Section Placement Pattern

For shop `itext_m_zcom_1422` at offset 630874 (0x9A05A):

**Sections BEFORE shop ID:**
```
Offset    Distance    Type         Content
627891    -2983      .items       9 items (including tournament_helm x4)
629039    -1835      .shopunits   Units section
629793    -1081      .spells      11 spells
630874     0         SHOP_ID      "itext_m_zcom_1422" (UTF-16 LE)
```

**Sections AFTER shop ID:**
```
631904    +1030      .items       4 items
632277    +1403      .shopunits   Units section
632387    +1513      .spells      3 spells
```

**Hypothesis:** Shop sections appear IMMEDIATELY BEFORE the shop ID in order:
1. `.items` section
2. `.shopunits` section
3. `.spells` section
4. Shop ID (UTF-16 LE)

Sections AFTER the shop ID likely belong to the NEXT shop.

## Verification Needed

Test shop: `itext_m_zcom_1422`

**Expected (from user):**
- Items: ~13 items including `tournament_helm`
- Spells: 32 spells
- Units: Unknown

**Found using -2983 bytes .items section:**
- 9 items including `tournament_helm x4` ✓

**Found using -1081 bytes .spells section:**
- 11 spells

**Issue:** Only 11 spells found, but user says 32 spells in-game.

**Possible causes:**
1. Wrong spell section (should use different one?)
2. Parsing error (not all spells extracted from section?)
3. Counting difference (user might be counting spell scrolls as separate items?)

## Test Strategy

1. Check if section at -1081 has more spells than parsed (parsing bug)
2. Check if user is counting `addon4_spell_rock_*` items as spells
3. Find pattern for which sections belong to which shop

## Section Markers

Found these markers within ±20KB of shop:

`.items`: 11 sections
`.spells`: 11 sections
`.shopunits`: 10 sections
`.shop`: 10 sections (same positions as `.shopunits`)

**Note:** `.shop` and `.shopunits` have identical positions, suggesting `.shopunits` is the actual marker name.

## Next Steps

1. ✅ Identify that shops have 3 product types
2. ✅ Parse quantities for each product
3. ⏳ Determine correct section assignment per shop
4. ⏳ Verify spell count matches in-game (32 expected)
5. ⏳ Test with multiple shops to confirm pattern
6. ⏳ Create final parser that extracts all product types correctly
