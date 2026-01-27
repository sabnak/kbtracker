# Hero Inventory Extraction Research

**Date:** 2026-01-26

## Objective

Extend SaveDataParser to extract hero inventory and equipment data from King's Bounty save files.

## Background

- Current parser extracts shop inventory data (items, spells, units, garrison)
- Hero inventory uses similar encoding but requires finding the correct sections
- Need to populate `SaveFileData.hero_inventory` with `GameObjectData` instances

## Research Files

1. **find_hero_inventory.py** - Scans for section markers and known item kb_ids
2. **analyze_item_patterns.py** - Analyzes item encoding patterns and clustering

## Known Item Encoding Patterns (from shop parsing)

### Pattern 1: Items Section
- Format: `[length:uint32][kb_id:ascii][...metadata...slruck...][length]["slot,quantity"]`
- Example: `slruck....2,4` = slot 2, quantity 4
- Used for equipment and consumables

### Pattern 2: Spells Section
- Format: `[length:uint32][kb_id:ascii][quantity:uint32]`
- Direct uint32 quantity after item name
- Used for spell scrolls

### Pattern 3: Units/Garrison Section
- Format: `strg[length:uint32][slash_separated_string]`
- String format: `"unit_name/quantity/unit_name/quantity/..."`
- Example: `"bowman/152/knight/25"`

## Next Steps

1. Run research scripts to identify hero inventory sections
2. Determine which encoding pattern(s) hero inventory uses
3. Identify section markers or boundaries for hero inventory
4. Implement parser methods to extract hero items
5. Update SaveDataParser.parse() to populate hero_inventory field
