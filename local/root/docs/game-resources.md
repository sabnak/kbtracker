# Game Resources

## Overview

Game resources are data files containing game content like items, units, spells, quests, and localization. These resources are stored in KFS archive files within the game's installation directory.

## Supported Games

This documentation covers the following King's Bounty games and their mods:

1. **King's Bounty: The Legend** (2008) - Russian: "King's Bounty. Легенда о рыцаре"
2. **King's Bounty: Armored Princess** - Russian: "King's Bounty: Принцесса в доспехах"
3. **King's Bounty: Crossworlds** - Russian: "King's Bounty: Перекрёстки миров"
4. **King's Bounty: Warriors of the North** - Russian: "King's Bounty: Воин Севера"
5. **King's Bounty: Dark Side** - Russian: "King's Bounty: Тёмная сторона"

**Community Mods**: These games have community-made mods that may:
- Add new entities (items, units, quests)
- Include additional resource files
- Expand or modify original game resources

## Resource Location

### Filesystem Structure

Game root directories are mounted in the application container at:

```
/data/<game_name>/
```

**Example**: King's Bounty: Dark Side resources are located at `/data/Darkside/`

### Directory Layout

```
/data/<game_name>/
├── sessions/
│   ├── base/           (may contain resource archives)
│   ├── <session_name>/ (main game resources)
│   │   ├── loc_*.kfs   (localization archives)
│   │   ├── ses.kfs     (game data archive)
│   │   └── ...
```

## KFS Archive Format

### What is KFS

KFS (`.kfs`) files are ZIP-based archives containing game resources. Despite the custom extension, they are standard ZIP archives.

**Verification**:
```bash
file /data/Darkside/sessions/darkside/loc_ses.kfs
# Output: Zip archive data, at least v2.0 to extract
```

### Extraction

KFS archives can be extracted using:
- Standard ZIP tools (`unzip`, 7-Zip, etc.)
- Project utility: `src/domain/game/utils/KFSExtractor.py`

## Resource Types

Game resources are organized into two main categories based on archive naming:

### 1. Localization Resources

**Archive Pattern**: `loc_*.kfs`

Contains translated text for game entities (item names, descriptions, quest text, etc.)

**Examples**:
- `loc_ses.kfs` - Russian localization
- `loc_ses_eng.kfs` - English localization
- `loc_ses_ger.kfs` - German localization
- `loc_ses_pol.kfs` - Polish localization

**Documentation**: See [localization.md](localization.md) for detailed extraction guide.

### 2. Game Data Resources

**Archive Pattern**: All other `.kfs` files (e.g., `ses.kfs`)

Contains game logic data:
- Numerical characteristics (stats, prices, levels)
- LUA scripts
- Images and textures
- Item definitions
- Unit definitions
- Quest data

**Format**: Mostly plain text files with custom syntax

**Documentation**: See [items.md](items.md) for item-specific extraction guide.

## kb_id Concept

### What is kb_id

`kb_id` (King's Bounty ID) is a unique string identifier assigned to every game entity:
- Items: `snake_belt`, `shield`, `addon4_orc_battle_hoe_2`
- Spells: `spell_dispell`
- Units: `snake`, `snake_green`, `snake_royal`
- And more

### Usage

kb_id is used to:
- Link resources across different files
- Reference entities in game logic
- Connect game data with localization
- Query database for specific entities

**Example**: An item with kb_id `shield` will have:
- Item definition in `item*.txt` files (inside `ses.kfs`)
- Localization entries with kb_id prefix `itm_shield_name`, `itm_shield_hint`, etc.
- Database record in `item` table with `kb_id = 'shield'`

## Database Structure

### Multi-Tenancy

Each game has its own PostgreSQL schema:
- Schema pattern: `game_<id>` (e.g., `game_19`)
- Game list stored in `public.game` table
- Extracted resources stored in game-specific schema tables

### Common Tables

| Table | Purpose | Documentation |
|-------|---------|---------------|
| `localization` | Translated text | [localization.md](localization.md) |
| `item` | Item definitions | [items.md](items.md) |
| `item_set` | Item set definitions | [items.md](items.md) |

## Workflow Example

Typical workflow for extracting item data:

1. Locate game directory: `/data/Darkside/`
2. Navigate to sessions: `/data/Darkside/sessions/darkside/`
3. Extract `ses.kfs` archive to access `item*.txt` files
4. Extract `loc_ses.kfs` (or language-specific) for item names/descriptions
5. Parse item files to extract properties
6. Parse localization files to extract text
7. Store in database tables `item` and `localization`
8. Query using kb_id to link items with their localized text

## Next Steps

- **For localization extraction**: See [localization.md](localization.md)
- **For item extraction**: See [items.md](items.md)
