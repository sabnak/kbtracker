# Complete Shop Structure - King's Bounty Save Files

## Shop Sections (4 Types)

Each shop location has up to 4 sections:

1. **Garrison** (`.garrison`) - Up to 3 unit slots for storing player's army
2. **Items** (`.items`) - Equipment and items for sale
3. **Units** (`.shopunits`) - Units/troops for hire
4. **Spells** (`.spells`) - Spells for purchase

## Section Order in Binary

Sections appear BEFORE the shop ID in this order:

```
[.garrison section]   ← Player's stored army (3 slots max)
[.items section]      ← Items for sale
[.shopunits section]  ← Units for hire
[.spells section]     ← Spells for purchase
[Shop ID UTF-16 LE]   ← "itext_m_<location>_<number>"
```

## Test Case: Shop `itext_m_zcom_1422`

```
Offset    Distance      Section
627802    -3072 bytes   .garrison
627891    -2983 bytes   .items
629039    -1835 bytes   .shopunits
629793    -1081 bytes   .spells
630874        0 bytes   Shop ID: "itext_m_zcom_1422"
```

This matches the game UI tabs:
- Tab 1 (Снаряжение) → .items
- Tab 2 (Магия) → .spells
- Tab 3 (Войска) → .shopunits
- Tab 4 (Гарнизон) → .garrison

## Data Formats

### 1. Garrison Format (DIFFERENT!)

Garrison uses a **slash-separated string** format:

```
"unit_name/quantity/unit_name/quantity/..."
```

**Example:**
```
"dread_eye/53/cyclop/27/gargoyle/159"
```

Parses to:
- dread_eye × 53
- cyclop × 27
- gargoyle × 159

**Structure:**
```
.garrison marker (9 bytes)
metadata
strg marker (4 bytes)
string length (4 bytes)
garrison string (N bytes)
```

### 2. Items/Units/Spells Format (SAME)

These three sections use the **entry-based format**:

```
4 bytes: name_length
N bytes: name (ASCII)
4 bytes: quantity
... metadata ...
[repeat]
```

**Parsing Strategy:**
- Scan entire section from marker to next section/shop ID
- Ignore count header (unreliable!)
- Validate each entry
- Stop at shop ID

## Validation Rules

### Valid ID Pattern
```python
pattern = r'^[a-z][a-z0-9_]*$'
```

### Invalid Metadata
Filter out these from items section:
- `upgrade/item1,item2/rndid/N`
- `use/N/item_add/scroll/scroll/spell/rndid/N`
- `item_count/N/victory/N/rndid/N`
- `map/N/image/picture/rndid/N`

## Complete Test Results

### Shop: `itext_m_zcom_1422`

#### Garrison (3/3 slots) ✅
```
dread_eye   × 53
cyclop      × 27
gargoyle    × 159
```

#### Items (9 items) ✅
```
addon4_dwarf_simple_belt  × 4
addon4_elf_bird_armor     × 4
addon4_elf_botanic_book   × 4
addon4_elf_fairy_amulet   × 4
addon4_human_life_cup     × 4
exorcist_necklace         × 4
fire_master_braces        × 4
moon_sword                × 4
tournament_helm           × 4
```

#### Spells (32 spells) ✅
```
spell_blind               × 1
spell_chaos_coagulate     × 2
spell_cold_grasp          × 2
spell_defenseless         × 1
spell_demonologist        × 1
spell_desintegration      × 4
spell_dispell             × 4
spell_dragon_arrow        × 2
spell_empathy             × 4
spell_fire_breath         × 3
spell_fire_shield         × 1
spell_ghost_sword         × 2
spell_gold_rush           × 4
spell_healing             × 6
spell_holy_rain           × 1
spell_horde_totem         × 1
spell_kamikaze            × 2
spell_life_stealer        × 2
spell_lull                × 7
spell_magic_source        × 2
spell_mine_field          × 2
spell_pain_mirror         × 2
spell_plague              × 1
spell_raise_dead          × 3
spell_revival             × 2
spell_scare               × 3
spell_shifted_time        × 2
spell_slow                × 1
spell_undertaker          × 3
spell_wasp_swarm          × 1
spell_weakness            × 1
spell_winter_dance        × 1
```

#### Units
Not yet tested (need to find shopunits section)

## Parser Status

✅ Garrison - Working
✅ Items - Working
✅ Spells - Working
⏳ Units - To be implemented

## Next Steps

1. Parse units section (.shopunits)
2. Create complete shop extractor for all shops
3. Generate JSON output with all 4 sections
4. Test with multiple shops
5. Integrate into main application
