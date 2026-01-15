# Investigation: Missing Shop in Dragondor Location

**Date**: 2026-01-15

## Problem Statement

ShopInventoryParser is failing to detect a shop in the dragondor location. The shop:
- Has no name in-game
- Doesn't display on the map
- Is still interactable
- Contains specific inventory (units and spells, no items)

**Known shops found**: dragondor_4, dragondor_5899, dragondor_5897

**Expected inventory of missing shop**:
- Items: none
- Units: bocman x1460, monstera x250, bear_white x156, demonologist x134
- Spells: dispell x2, gifts x2, shroud x2, dragon_slayer, pacifism x2, advspell_summon_dwarf x1
- Garrison: none

**Hypothesis**: The shop may not have the `itext_` prefix that the current parser searches for.

**Save file**: `/app/tests/game_files/saves/1768403991`

## Investigation Steps

### Step 1: Review Parser Logic

Reviewed ShopInventoryParser.py at `/app/src/utils/parsers/save_data/ShopInventoryParser.py`.

Key finding: The parser searches BACKWARDS from shop identifiers using `_find_preceding_section()` method.

### Step 2: Parse Save File and Check for Shop

Ran shop extractor on save file `/app/tests/game_files/saves/1768403991`:
- Total shops found: 315
- Shops in dragondor: dragondor_4, dragondor_5899, dragondor_5897, and many others
- No shop found with bocman x1460 inventory

### Step 3: Search Raw Decompressed Data

Decompressed save file to `/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin`.

Found bocman/1460 at position 669460 (0xa3714) in .shopunits section.

### Step 4: Trace Shop Structure

Found the shop structure at position 669222 (building_trader@293):
- Location: m_portland_dark
- Label references: itext_m_portland_dark_6533_name, itext_m_portland_dark_6533_terr
- Shop identifier pattern: itext_m_portland_dark_6533

Structure layout:
```
[Position 669189] lt: m_portland_dark
[Position 669222] building_trader@293
[Position 669413] .shopunits: bocman/1460/monstera/250/bear_white/156/demonologist/134
[Position 669649] .spells: (spell data)
[Position 669782] .temp
[Position 669930] Next shop (dragondor, building_trader@31)
```

### Step 5: Root Cause Identified

**CRITICAL FINDING**: The shop IS detected by the parser as `m_portland_dark_6533`, but with WRONG inventory!

Parser extracts this shop data:
```json
m_portland_dark_6533: {
  units: [
    {name: skeleton, quantity: 70},
    {name: zombie, quantity: 20},
    {name: ghost2, quantity: 2}
  ]
}
```

Expected data (not found):
```json
m_portland_dark_6533: {
  units: [
    {name: bocman, quantity: 1460},
    {name: monstera, quantity: 250},
    {name: bear_white, quantity: 156},
    {name: demonologist, quantity: 134}
  ],
  spells: [
    {name: dispell, quantity: 2},
    {name: gifts, quantity: 2},
    {name: shroud, quantity: 2},
    {name: dragon_slayer, quantity: 1},
    {name: pacifism, quantity: 2},
    {name: advspell_summon_dwarf, quantity: 1}
  ]
}
```

### Step 6: Analyze Position Timeline

Timeline analysis reveals the problem:
```
Position 668370: .shopunits with skeleton/70/zombie/20/ghost2/2
Position 668575: itext_m_portland_dark_6533 identifier (parser search starts here)
Position 669413: .shopunits with bocman/1460/monstera/250/... (CORRECT DATA)
```

**Root Cause**: The parser searches BACKWARDS from the shop identifier (position 668575) using `_find_preceding_section()`. It finds the .shopunits at position 668370 (which contains skeleton/zombie/ghost2) instead of the correct .shopunits at position 669413 (which contains bocman/1460).

The correct shop data is AFTER the shop identifier, not before it.


## Analysis of Save File Structure

### Multiple Shop Identifier Occurrences

Investigation revealed that shop identifiers like `itext_dragondor_4` and `itext_m_portland_dark_6533` appear MULTIPLE times in the save file.

**dragondor_4**: 13 occurrences
**m_portland_dark_6533**: 9 occurrences

The parser's deduplication logic (`_find_all_shop_ids` method):
- Uses `seen_shop_ids` set to track already-found shop IDs
- Keeps only the FIRST occurrence found during chunk scanning
- Due to chunk overlap, may not always find the earliest occurrence in file

### Parser Architecture Issue

The parser is designed with the assumption that shop sections (.shopunits, .items, .spells, .garrison) appear BEFORE the shop identifier in the file. This is enforced by:

1. `_find_preceding_section()` - searches BACKWARDS from shop identifier
2. `_section_belongs_to_shop()` - validates no other shop ID exists between section and identifier

However, the save file structure shows TWO patterns:

**Pattern A: Sections BEFORE identifier** (works correctly)
```
[.shopunits with data]
[itext_shop_id]
```

**Pattern B: Sections AFTER identifier** (parser fails)
```
[itext_shop_id]  <- Parser searches backwards from here
[.shopunits with data]  <- Correct data is here, but parser looks backwards
```

### Case Study: m_portland_dark_6533

Position 668575: `itext_m_portland_dark_6533` (parser starts here)
Position 668370: .shopunits with skeleton/zombie/ghost2 (found by backwards search)
Position 669222: building_trader@293 (actual building definition)
Position 669413: .shopunits with bocman/1460 (CORRECT DATA, but after identifier!)

The parser finds position 668370 because it searches backwards, but that .shopunits belongs to a DIFFERENT shop. The correct .shopunits at position 669413 is never found because it's AFTER the identifier.

### Data Loss Patterns

Two types of data loss occur:

1. **Wrong inventory attribution**: Parser finds inventory from a previous shop
   - Example: m_portland_dark_6533 gets skeleton/zombie instead of bocman/monstera
   
2. **Missing inventory**: Parser finds no sections backwards and returns empty
   - Example: dragondor_4 at position 658175 has no .shopunits before it

## Conclusion

**Root Cause**: The parser architecture assumes shop inventory sections appear BEFORE the shop identifier, but the save file format places them AFTER the building definition, which includes the shop identifier labels.

**Impact**: 
- Shops with inventory sections after their identifier get wrong or empty data
- The missing

## Updated Investigation: Dragondor Location Shops

### Verification of Hypothesis

The original hypothesis that the shop lacks the  prefix is **INCORRECT**.

Through previous investigation, we discovered:
1. The shop IS detected with identifier 
2. The shop has the expected  prefix
3. However, the parser extracts WRONG inventory data

### Search for bocman/monstera Sections

Let me search the decompressed save file for all .shopunits sections containing bocman.

