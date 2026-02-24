# Hero Inventory Research Findings

**Date:** 2026-01-26
**Save File:** `tests/game_files/saves/inventory1769382036`

## Summary

Hero inventory is stored in `.items` sections that are part of the hero's **castle structure**, NOT as standalone inventory sections.

## Key Findings

### 1. Hero Inventory Structure

Hero inventory uses the **same encoding as shop `.items` sections**:
- Format: `[length:uint32][kb_id:ascii][metadata...slruck[length]["slot,quantity"]...]`
- Example: `knight_shield` → `slruck` contains "1,1" (slot=1, quantity=1)
- Stackable items: `addon4_3_crystal` → `slruck` contains "8,20" (slot=8, quantity=20)

### 2. Distinguishing Pattern

**Hero `.items` sections** are preceded by castle markers (within ~2000 bytes):
```
.castleruler1
  flags
  strg: "father"
.castleunits
  flags
  strg: "goblin/3/4/archer/5/6/wolf/1/1"  ← castle garrison units
.items  ← HERO INVENTORY STARTS HERE
```

**Shop `.items` sections** are preceded by:
```
template@NUMBER
  auid
  pos
  flags
  vars
.actors
  flags
  strg: [encoded shop ID]
.items  ← SHOP INVENTORY STARTS HERE
```

### 3. Hero Inventory Sections Found

In test save file, **6 hero `.items` sections** were identified:

| Position | Distance to Castle Marker | Sample Items |
|----------|---------------------------|--------------|
| 119932   | ~2000 bytes               | knight_shield, hunter_gloves |
| 139551   | ~2000 bytes               | knight_sword |
| 546889   | ~2000 bytes               | ogr_belt |
| 548957   | ~2000 bytes               | addon4_3_crystal (qty: 20) |
| 569249   | ~2000 bytes               | tournament_helm |
| 621517   | ~2000 bytes               | vampire_ring |

### 4. Quantity Encoding

Items use `slruck` metadata with format: `"slot,quantity"`
- Non-stackable equipment: `"1,1"` (quantity = 1)
- Stackable consumables: `"8,20"` (quantity = 20)

### 5. Section Boundaries

Hero `.items` sections end when:
- Next section marker appears (`.spells`, `.shopunits`, `.temp`, etc.)
- Next `.items` section begins
- Shop identifier appears (`itext_`, `building_trader@`)

## Implementation Strategy

### Step 1: Find Castle Markers

```python
def _find_castle_markers(self, data: bytes) -> list[int]:
    """Find all .castleruler1 markers indicating hero castles"""
    positions = []
    pos = 0
    while pos < len(data):
        pos = data.find(b'.castleruler1', pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    return positions
```

### Step 2: Find .items After Castle

```python
def _find_items_after_castle(self, data: bytes, castle_pos: int) -> Optional[int]:
    """Find .items section after castle marker (within 3000 bytes)"""
    search_end = min(len(data), castle_pos + 3000)
    chunk = data[castle_pos:search_end]

    items_pos = chunk.find(b'.items')
    if items_pos != -1:
        return castle_pos + items_pos
    return None
```

### Step 3: Reuse Existing Items Parser

The existing `_parse_items_section()` method can be reused! It already handles:
- Length-prefixed ASCII item kb_ids
- `slruck` metadata parsing
- Quantity extraction

### Step 4: Aggregate All Hero Items

```python
def _parse_hero_inventory(self, data: bytes) -> list[GameObjectData]:
    """Parse all hero inventory sections"""
    all_items = []

    # Find all castle markers
    castle_markers = self._find_castle_markers(data)

    for castle_pos in castle_markers:
        # Find .items section after castle
        items_pos = self._find_items_after_castle(data, castle_pos)
        if not items_pos:
            continue

        # Find section end
        section_end = self._find_section_end(data, items_pos, items_pos + 10000)

        # Parse items (reuse existing method)
        items = self._parse_items_section(data, items_pos, section_end)

        # Convert to GameObjectData
        for kb_id, quantity in items:
            all_items.append(GameObjectData(kb_id=kb_id, quantity=quantity))

    return all_items
```

## Edge Cases

1. **Multiple castles**: Hero might have multiple castles, each with inventory
2. **Empty inventory**: Castle exists but no `.items` section
3. **Duplicate items**: Same item in different castle sections (should aggregate quantities)

## Testing

Test save file `inventory1769382036` should extract:
- `knight_shield` (quantity: 1)
- `knight_sword` (quantity: 1)
- `tournament_helm` (quantity: 1)
- `vampire_ring` (quantity: 1)
- `ogr_belt` (quantity: 1)
- `addon4_3_crystal` (quantity: 20)
- Additional items found in all 6 hero `.items` sections

## Next Steps

1. ✅ Pattern identified and documented
2. ⏳ Implement parser methods
3. ⏳ Test with save file
4. ⏳ Handle edge cases (multiple castles, duplicates)
5. ⏳ Integrate with main parser
