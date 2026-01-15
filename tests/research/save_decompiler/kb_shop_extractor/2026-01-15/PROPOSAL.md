# Proposal: Fix ShopInventoryParser Directional Search Issue

**Date**: 2026-01-15

## Problem Summary

ShopInventoryParser searches BACKWARDS from shop identifiers, but shop inventory sections can appear AFTER the identifier in the save file structure, causing wrong or missing inventory data.

## Proposed Solution

Modify the parser to search in BOTH directions from the shop identifier and intelligently select the correct sections.

### Implementation Strategy

#### Option 1: Bidirectional Section Search (Recommended)

Modify `_find_preceding_section()` to also check forward:

```python
def _find_section_near_shop(
    self,
    data: bytes,
    marker: bytes,
    shop_pos: int,
    max_distance: int = 5000
) -> Optional[int]:
    """
    Find section marker near shop ID, searching both directions
    
    Prioritize sections that:
    1. Are within max_distance
    2. Have no other shop IDs between section and target shop
    3. Are closer to the shop position
    """
    # Search backwards
    preceding_pos = self._find_preceding_section(data, marker, shop_pos, max_distance)
    
    # Search forwards  
    following_pos = self._find_following_section(data, marker, shop_pos, max_distance)
    
    # Validate both candidates
    candidates = []
    
    if preceding_pos and self._section_belongs_to_shop(data, preceding_pos, shop_pos):
        candidates.append(('before', preceding_pos))
    
    if following_pos and self._section_belongs_to_shop_forward(data, shop_pos, following_pos):
        candidates.append(('after', following_pos))
    
    # Return the closest valid section
    if not candidates:
        return None
    
    # Prefer forward sections if both exist (more reliable)
    for direction, pos in candidates:
        if direction == 'after':
            return pos
    
    return candidates[0][1]
```

#### Option 2: Parse from Building Definitions

Instead of searching from `itext_` identifiers, parse from `building_trader@` entries:

1. Find all `building_trader@` entries
2. Extract location (`lt`) field
3. Find sections AFTER the building definition
4. Construct shop_id from location + building number

This approach is more reliable because:
- Building definitions come before their sections
- No ambiguity about which sections belong to which shop
- Follows the actual save file structure

### New Methods Needed

```python
def _find_following_section(
    self,
    data: bytes,
    marker: bytes,
    shop_pos: int,
    max_distance: int = 5000
) -> Optional[int]:
    """Search forward from shop position for section marker"""
    search_end = min(len(data), shop_pos + max_distance)
    pos = data.find(marker, shop_pos, search_end)
    return pos if pos != -1 else None


def _section_belongs_to_shop_forward(
    self,
    data: bytes,
    shop_pos: int,
    section_pos: int
) -> bool:
    """Verify no other shop ID exists between shop and section when searching forward"""
    chunk = data[shop_pos:section_pos]
    
    try:
        text = chunk.decode('utf-16-le', errors='ignore')
        # Look for other itext_ patterns, but exclude the current shop's multiple labels
        other_shops = re.findall(r'itext_([-\w]+)_(\d+)', text)
        
        # If we find different shop IDs, section doesn't belong to this shop
        if len(set(other_shops)) > 1:
            return False
    except:
        pass
    
    return True
```

## Testing Strategy

1. Create test with known shops that have sections after identifier
2. Verify m_portland_dark_6533 extracts bocman/1460 correctly
3. Verify dragondor_4 extracts correct inventory
4. Regression test: ensure existing working shops still work

## Risks and Mitigation

**Risk**: Forward search might find sections from the next shop  
**Mitigation**: `_section_belongs_to_shop_forward()` validates no intervening shop IDs

**Risk**: Breaking existing functionality  
**Mitigation**: Comprehensive test suite with before/after comparisons

## Alternative Approach

If bidirectional search proves complex, consider:
- Parse by building_trader entries instead of itext_ identifiers
- This aligns with the actual save file structure
- May require larger refactoring but more robust long-term

