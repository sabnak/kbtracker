# Hero Inventory Extraction - FINAL FINDINGS

**Date:** 2026-01-26
**Save File:** `tests/game_files/saves/inventory1769382036`

## Critical Discovery

**Hero inventory does NOT have a separate `.items` section!**

All hero items (inventory + equipped) are stored in the SAME `.items` section as achievements and companions.

## Structure

**Single `.items` section at position 909699 contains:**

1. **Achievements** (~positions 909699-915000)
   - Format: `achievement_*`
   - Example: `achievement_connoisseur_of_antiquities_1`

2. **Companions & Special Items** (~positions 915000-917270)
   - Format: `addon3_companion_*` with `slbody....wife0/wife1`
   - Example: `addon3_companion_barristan_witt_3_a`, `addon3_companion_lucia_3_b`

3. **Hero Inventory & Equipment** (starts at position 917270)
   - Format: Same as shop items with `slruck` metadata
   - Example: `addon3_magic_ingridients` with `slruck....197,1`
   - Contains **>200 items** including:
     - Inventory items
     - Hero equipped items
     - Companion equipped items

## Item Encoding

**Same format as shop items:**
```
[length:uint32][kb_id:ascii][metadata...]
  count: 01 00 00 00
  lvars: [rndid/...]
  slruck: [length:uint32]["slot,quantity"]
```

**Example:**
```
addon3_magic_ingridients
  count: 1
  lvars: count1/5/choice/2/rndid/1472723701
  slruck: "197,1"  → slot=197, quantity=1
```

## Implementation Strategy

### Step 1: Find Hero Inventory `.items` Section

Hero inventory is in a `.items` section that:
- Contains both `achievement_*` items AND regular items
- Is preceded by `hero@1` marker (around position 909532)
- Starts at position ~909699

**Detection method:**
```python
def _find_hero_inventory_section(self, data: bytes) -> Optional[int]:
    """
    Find .items section containing hero inventory

    Hero inventory shares .items section with achievements.
    Look for .items section preceded by hero@ marker.
    """
    pos = 0
    while pos < len(data):
        # Find hero@ marker
        hero_pos = data.find(b'hero@', pos)
        if hero_pos == -1:
            break

        # Search forward for .items
        search_end = min(len(data), hero_pos + 5000)
        items_pos = data.find(b'.items', hero_pos, search_end)

        if items_pos != -1:
            return items_pos

        pos = hero_pos + 1

    return None
```

### Step 2: Parse ALL Items from Section

Reuse existing `_parse_items_section()` to extract all items (achievements + hero inventory).

```python
# Find section end
section_end = self._find_section_end(data, items_pos, items_pos + 200000)

# Parse all items (achievements + hero inventory)
all_items = self._parse_items_section(data, items_pos, section_end)
```

### Step 3: Filter Valid Items

Filter out achievements and metadata keywords:

```python
def _filter_hero_items(self, items: list[tuple[str, int]]) -> list[GameObjectData]:
    """
    Filter hero inventory items from achievements and metadata

    :param items:
        List of (kb_id, quantity) tuples from .items section
    :return:
        List of valid hero inventory items as GameObjectData
    """
    hero_items = []

    for kb_id, quantity in items:
        # Skip achievements
        if kb_id.startswith('achievement_'):
            continue

        # Skip metadata keywords
        if kb_id in self.METADATA_KEYWORDS:
            continue

        # Skip if not valid item ID format
        if not self._is_valid_id(kb_id):
            continue

        # All remaining items are hero inventory
        hero_items.append(GameObjectData(kb_id=kb_id, quantity=quantity))

    return hero_items
```

### Step 4: Database Validation (Optional)

For uncertain items, validate against database:

```python
# Query: SELECT * FROM game_14.item WHERE kb_id='<kb_id>'
# If exists → valid item
# If not exists → skip
```

## Expected Results

Test save `inventory1769382036` should extract **>200 items** including:

**First 5 inventory items:**
- `addon3_magic_ingridients` (quantity: 1)
- `kerus_sword` (quantity: 1)
- `addon4_human_battle_mage_braces` (quantity: 1)
- `flame_necklace` (quantity: 1)
- `addon4_demon_pandemonic_gloves` (quantity: 1)

**Middle items:**
- `addon4_spell_rock_holy_rain_100` (quantity: 3)
- `addon4_spell_rock_resurrection_80` (quantity: 6)
- `addon4_spell_rock_life_stealer_100` (quantity: 2)
- `addon4_spell_rock_fire_shield_200` (quantity: 2)
- `addon4_turtle_shield` (quantity: 1)

**Last 5 items:**
- `addon3_shield_tristrem_founder` (quantity: 1)
- `addon3_quest_hobo` (quantity: 626)
- `addon3_quest_baron_ponton` (quantity: 1)
- `addon3_quest_weapon_cargo` (quantity: 6)
- `addon3_quest_pow` (quantity: 5767)

**Hero equipped items:**
- `battlemage_helm`, `pictures_book`, `addon4_human_archmage_boots`, `addon4_neutral_beholder_amulet_3`, `addon4_elf_poison_staff`

**Companion 1 equipped:**
- `arhmage_staff`, `destructor_gloves`, `sword_full_moon`, `wizard_mantle`

**Companion 2 equipped:**
- `addon4_inventor_dwarf_helmet`

**Companions themselves (may or may not be included):**
- `addon3_companion_barristan_witt_3_a`
- `addon3_companion_lucia_3_b`

## Critical Implementation Notes

1. **No separate hero inventory section** - it's all in one `.items` section with achievements
2. **Reuse existing parser** - `_parse_items_section()` already handles the format
3. **Simple filtering** - just skip `achievement_*` and metadata keywords
4. **Quantity from slruck** - parse "slot,quantity" format (e.g., "197,1" → quantity=1)
5. **Large section** - may contain 300+ items total, need to parse entire section

## Section Boundaries

- **Start:** Position 909699 (`.items` marker)
- **End:** Find next section marker or ~200KB after start
- **Hero items start:** Around position 917270 (after achievements and companions)
- **Total items:** >200 hero items + ~100 achievements = ~300+ items total
