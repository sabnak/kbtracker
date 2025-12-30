# PostgreSQL Schema Migration - Remaining Work

## Overview

The core schema migration is **90% complete**. The database layer, repository layer, domain layer, and service layer have all been successfully migrated. What remains is updating the web layer (routes and templates) and parser utilities.

---

## 1. Update FastAPI Routes (HIGH PRIORITY)

### Pattern to Apply

All game-related routes need to:
1. Add `GameContext` dependency via `get_game_context()`
2. Set the context variable: `_game_context.set(game_context)`
3. Remove `game_id` parameters from service calls

### Files to Update

#### `src/web/games/routes.py`

**Routes requiring updates:**

```python
from src.web.dependencies.game_context import get_game_context, GameContext
from src.domain.CrudRepository import _game_context

# Pattern for each route:
@router.get("/games/{game_id}/items")
@inject
async def list_items(
    request: Request,
    game_context: GameContext = Depends(get_game_context),  # ADD THIS
    query: str = Query(default=""),
    item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
):
    _game_context.set(game_context)  # ADD THIS at start of route

    # REMOVE game_id parameter from service calls:
    items = item_tracking_service.get_items_with_sets(  # Remove game_id
        name_query=query,
        # ... other params
    )
```

**Specific routes to update:**
- `GET /games/{game_id}/items` - list items with filters
- `POST /games/{game_id}/scan` - scan game files
- `GET /games/{game_id}/shops-grouped` - get shops by location
- `GET /games/{game_id}/profiles` - list profiles for game

**Service method signature changes:**
- `item_tracking_service.get_items_with_sets(game_id, ...)` → remove `game_id`
- `item_tracking_service.search_items(game_id, query)` → `search_items(query)`
- `item_tracking_service.get_locations(game_id)` → `get_locations()`
- `item_tracking_service.get_shops_grouped_by_location(game_id)` → `get_shops_grouped_by_location()`
- `item_tracking_service.get_available_levels(game_id)` → `get_available_levels()`
- `item_tracking_service.get_available_item_sets(game_id)` → `get_available_item_sets()`

#### `src/web/profiles/routes.py`

**Routes requiring game_id in path:**
- `POST /profiles` → `POST /games/{game_id}/profiles`
- `DELETE /profiles/{profile_id}` → `DELETE /games/{game_id}/profiles/{profile_id}`

**Service method changes:**
- `profile_service.create_profile(name, game_id)` → `create_profile(name)`

#### `src/web/api/routes.py`

**All profile API routes need game_id added to path:**
- `/api/profiles/{profile_id}/tracked` → `/api/games/{game_id}/profiles/{profile_id}/tracked`
- `/api/profiles/{profile_id}/track-item` → `/api/games/{game_id}/profiles/{profile_id}/track-item`
- `/api/profiles/{profile_id}/untrack-item` → `/api/games/{game_id}/profiles/{profile_id}/untrack-item`
- `/api/profiles/{profile_id}/update-item-count` → `/api/games/{game_id}/profiles/{profile_id}/update-item-count`

**Service method changes:**
- `item_tracking_service.get_all_items_with_tracked_shops(profile_id, game_id)` → `get_all_items_with_tracked_shops(profile_id)`

**Pattern:**
```python
@router.get("/api/games/{game_id}/profiles/{profile_id}/tracked")
@inject
async def get_tracked_items(
    profile_id: int,
    game_context: GameContext = Depends(get_game_context),
    item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"])
):
    _game_context.set(game_context)
    items = item_tracking_service.get_all_items_with_tracked_shops(profile_id)
    # ... rest of route
```

---

## 2. Update Templates (MEDIUM PRIORITY)

### Files to Update

**Primary templates:**
- `src/web/templates/pages/index.html` - Profile list and delete links
- `src/web/templates/pages/item_list.html` - Item filtering form, shop links
- `src/web/templates/pages/game_list.html` - Game links
- `src/web/templates/components/profile_selector.html` - Profile links

### Changes Required

**Pattern for route links:**
```html
<!-- OLD: -->
<a href="/profiles/{{ profile.id }}/delete">Delete</a>

<!-- NEW: -->
<a href="/games/{{ game_id }}/profiles/{{ profile.id }}/delete">Delete</a>
```

**Pattern for API calls:**
```javascript
// OLD:
fetch(`/api/profiles/${profileId}/track-item`, ...)

// NEW:
fetch(`/api/games/${gameId}/profiles/${profileId}/track-item`, ...)
```

**Forms need game_id:**
```html
<!-- Profile creation form -->
<form action="/games/{{ game_id }}/profiles" method="post">
    <!-- ... -->
</form>
```

---

## 3. Update Parser Utilities (LOW PRIORITY)

These parsers create entities and should not include game_id in constructors.

### `src/domain/game/utils/KFSItemsParser.py`

**Changes:**
- Constructor: Remove `game_id` parameter
- `parse()` method: Create `Item` entities without `game_id` field

**Before:**
```python
def __init__(self, sessions_path: str, language: str, game_id: int):
    self._game_id = game_id

item = Item(
    id=0,
    game_id=self._game_id,  # REMOVE
    kb_id=kb_id,
    # ...
)
```

**After:**
```python
def __init__(self, sessions_path: str, language: str):
    # No game_id needed

item = Item(
    id=0,
    kb_id=kb_id,
    # ...
)
```

### `src/domain/game/utils/KFSLocationsAndShopsParser.py`

**Changes:**
- Constructor: Remove `game_id` parameter
- `parse()` method: Create `Location` and `Shop` entities without `game_id`

**Pattern same as above:**
```python
location = Location(
    id=0,
    # game_id=self._game_id,  # REMOVE
    kb_id=location_kb_id,
    name=location_name
)
```

### `src/domain/game/utils/KFSLocalizationParser.py`

**Changes:**
- `parse()` method signature: Remove `game_id` parameter
- Create `Localization` entities without `game_id`

**Before:**
```python
def parse(self, game_id: int, sessions_path: str, ...) -> list[Localization]:
    localization = Localization(
        id=0,
        game_id=game_id,  # REMOVE
        kb_id=kb_id,
        # ...
    )
```

**After:**
```python
def parse(self, sessions_path: str, ...) -> list[Localization]:
    localization = Localization(
        id=0,
        kb_id=kb_id,
        # ...
    )
```

---

## 4. Testing Strategy (CRITICAL)

### Manual Testing Checklist

1. **Create new game**
   - Verify schema is created (`SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'game_%'`)
   - Verify all tables exist in schema

2. **Scan game files**
   - Set game context in route
   - Verify data is saved to correct schema
   - Check items, locations, shops, localizations, item_sets

3. **Create profile**
   - Verify profile is created in game schema (not public)
   - Check that profile belongs to correct game

4. **Track items in shops**
   - Verify shops_has_items records go to correct schema
   - Test with multiple profiles in same game

5. **Multi-tab support**
   - Open two different games in different browser tabs
   - Verify each tab operates on correct schema
   - Verify no cross-contamination

6. **Delete game**
   - Verify entire schema is dropped
   - Verify game record removed from public.game
   - Verify cascade cleanup

### Integration Tests

Consider adding:
```python
def test_schema_isolation():
    """Test that two games have isolated data"""
    # Create game 1, scan files
    # Create game 2, scan files
    # Verify game 1 items != game 2 items
    # Verify schemas are separate
```

---

## 5. Rollback Plan

If issues arise:

```bash
# Immediate rollback
git checkout main
# Restart application - uses old schema structure

# If new schemas were created, clean up:
DROP SCHEMA game_1 CASCADE;
DROP SCHEMA game_2 CASCADE;
# etc.
```

**Safety:** The old public schema tables remain untouched, so rollback is instant.

---

## Estimated Effort

- **Routes updates:** 2-3 hours (pattern is repetitive)
- **Template updates:** 1-2 hours (search/replace with validation)
- **Parser updates:** 30 minutes (straightforward removals)
- **Testing:** 2-3 hours (thorough validation)

**Total:** ~6-8 hours of focused work

---

## Priority Order

1. **Update routes** (blocks everything)
2. **Update parser utilities** (needed for scanning)
3. **Update templates** (UI functionality)
4. **Comprehensive testing** (validation)

---

## Success Criteria

- [ ] All routes inject GameContext and set _game_context
- [ ] All service calls no longer pass game_id
- [ ] All templates use new route paths with game_id
- [ ] Parser utilities create entities without game_id
- [ ] Manual testing passes all checklist items
- [ ] Multi-tab support works (different games in different tabs)
- [ ] Game deletion properly drops schema
- [ ] No errors in console or logs

---

## Notes

- The hardest work is done (42 files already migrated)
- Remaining work follows clear, repetitive patterns
- Each route/template update is independent
- Can be completed incrementally
- Rollback is trivial if needed
