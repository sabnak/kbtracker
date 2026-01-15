# Investigation Findings: ID 807991996 and building_trader@31

## Summary

After comprehensive investigation of save file `/app/tests/game_files/saves/1768403991`, I can confirm:

### Fact 1: building_trader@31 Details
- **Location**: dragondor
- **Position in save**: 669916
- **Inventory**:
  - Units: bocman x1460, monstera x250, bear_white x156, demonologist x134
  - Spells: dispell x2, gifts x2, shroud x2, dragon_slayer x1, pacifism x2, advspell_summon_dwarf x1
- **Trader Name**: NONE (no entry in lookup table)
- **Parser ID**: `dragondor_building_trader_31`

### Fact 2: ID 807991996 Details
- **Appears in save file**: Only ONCE as ASCII text in the trader name lookup table
- **Position**: 2,168,657 (in lookup table section 2,160,000-2,180,000)
- **Lookup entry**: `building_trader@818   se       	   807991996`
- **Maps to**: `m_inselburg_actor_807991996` (building_trader@818)
- **Inventory**: EMPTY (no units, no spells, no items)

### Fact 3: No Connection in Save File
- `building_trader@31` does NOT have ID `807991996` anywhere in the save file
- `building_trader@31` does NOT appear in the trader name lookup table
- The ID `807991996` only exists as ASCII text associated with `building_trader@818`
- Searched in multiple formats:
  - ASCII text: Found only with @818
  - Little-endian binary: NOT found anywhere
  - Big-endian binary: NOT found anywhere
  - Within 1000 bytes of @31: NOT found

## Investigation Steps Taken

1. **Comprehensive ID Search**: Searched entire save file for `807991996` in:
   - ASCII text format
   - Little-endian 32-bit integer (0xbcfa2830)
   - Big-endian 32-bit integer (0x3028fabc)
   - Result: Found ONLY once as ASCII in lookup table with @818

2. **Location Tag Analysis**: Found 4 location tags in the area:
   - Position 668141: "dragondor" → building_trader@28
   - Position 669193: "m_portland_dark" → building_trader@293
   - Position 669893: "dragondor" → building_trader@31 (closest to @31, only -23 bytes)
   - Position 670209: "m_portland_dark" → building_trader@318

3. **AUID Field Check**: Examined `auid` fields near building markers:
   - building_trader@31: auid = 50331649 (not 807991996)
   - building_trader@818: auid = 50331654 (not 807991996)
   - These are sequential instance IDs, not trader name localization IDs

4. **Lookup Table Analysis**: Extracted 79 building_trader entries:
   - Pattern: `building_trader@{num} ... se ... {trader_id}`
   - building_trader@31: NOT in lookup table
   - building_trader@818: IN lookup table with ID 807991996

5. **Inventory Verification**: Confirmed:
   - Only ONE shop has bocman quantity > 1000: dragondor_building_trader_31
   - m_inselburg_actor_807991996 (building_trader@818) has empty inventory

## Possible Explanations for User's Observation

Since you stated "I SEE It IN game" for building_trader@31 with ID 807991996, but the save file shows otherwise, possible explanations:

1. **Different Save File**: You might be viewing a different save file in-game than `/app/tests/game_files/saves/1768403991`

2. **Shop Confusion**: You might be viewing building_trader@818 (which does have ID 807991996) but thought it was @31

3. **Game Display vs Storage**: The game might display or calculate trader IDs differently than they're stored in the save file

4. **Game Configuration Files**: The ID mapping might exist in game resource files (not the save file)

5. **Dynamic ID Assignment**: The game might assign trader IDs dynamically based on some formula we haven't discovered

## Conclusion

In save file `1768403991`:
- **dragondor_building_trader_31** has bocman inventory but NO trader name ID
- **m_inselburg_actor_807991996** (building_trader@818) has the ID but EMPTY inventory
- These are two completely different shops in different locations

The parser (ShopInventoryParser2.py) is working correctly based on what's in the save file.
