# Units

## Overview

Units are creatures and characters that can be recruited, fought, or encountered in the game. Each unit has a class (pawn or chesspiece), combat parameters, and various attributes defining their behavior in battle.

## Database Mapping

### Unit Table

**Table**: `unit` (in game-specific schema, e.g., `game_1.unit`)
**Entity**: `Unit`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `kb_id` | String | Unique in-game identifier for the unit |
| `unit_class` | String | Unit classification: "pawn" or "chesspiece" |
| `params` | JSONB | Flexible storage for all unit parameters (arena_params, features, etc.) |

### Unit Class

Units are classified into two types:

| Class | Description |
|-------|-------------|
| `pawn` | Regular combat units that participate in battles |
| `chesspiece` | Special units with unique abilities or roles |

**Note**: Units with `class=spirit` are automatically filtered out during extraction as they are internal game entities not meant for tracking.

## Archive Location

### Location

Units are stored in the main game data archive:

```
/data/<game_name>/data/data.kfs
```

Specifically in subdirectories like:
```
/data/<game_name>/data/Creatures/
/data/<game_name>/data/Darkside/
```

### File Pattern

Unit definitions are stored in `.atom` files matching the pattern:

```
<unit_kb_id>.atom
```

**Examples**:
- `bowman.atom`
- `knight.atom`
- `dark_giant.atom`
- `snake.atom`

## Unit File Format

### Atom File Structure

Units use the `.atom` file format, which is a key-value structure with nested sections:

```
main {
    class=chesspiece
    level=1
    race=human
}

arena_params {
    health=100
    speed=3
    attack=10
    features_hints=feature1,feature2,feature3
    attacks=melee,special
}
```

### Example: Bowman Unit

```
main {
    class=chesspiece
    level=1
    size=1
    min_speed=2
    max_speed=3
    race=human
    exp_level=1
}

arena_params {
    health=22
    mana=0
    speed=3
    morale=0
    attack=5
    defense=1
    intellect=1
    bless_power=0
    min_damage=1
    max_damage=2
    talents=0
    features_hints=shooter,living,male,noans
    attacks=range
    priority=40
}
```

### Example: Dark Giant Unit

```
main {
    class=chesspiece
    level=3
    size=2
    min_speed=1
    max_speed=2
    race=demon
    exp_level=1
}

arena_params {
    health=200
    mana=0
    speed=1
    morale=0
    attack=15
    defense=10
    intellect=1
    bless_power=0
    min_damage=25
    max_damage=40
    talents=0
    features_hints=living,male,large,demon_blood
    attacks=melee,stomp
    priority=50
}
```

## Properties of Interest

### Main Section

The `main` section contains core unit metadata:

| Property | Type | Description | Stored in DB |
|----------|------|-------------|--------------|
| `class` | String | Unit class (pawn, chesspiece, spirit) | Yes (as unit_class) |
| `level` | Integer | Unit tier/level | Yes (in params JSONB) |
| `race` | String | Unit race (human, elf, dwarf, etc.) | Yes (in params JSONB) |
| `size` | Integer | Unit size on battlefield | Yes (in params JSONB) |
| `min_speed` | Integer | Minimum initiative | Yes (in params JSONB) |
| `max_speed` | Integer | Maximum initiative | Yes (in params JSONB) |
| `exp_level` | Integer | Experience level | Yes (in params JSONB) |

### Arena Params Section

The `arena_params` section contains combat statistics and abilities:

| Property | Type | Description | Stored in DB |
|----------|------|-------------|--------------|
| `health` | Integer | Hit points | Yes (in params JSONB) |
| `mana` | Integer | Mana points | Yes (in params JSONB) |
| `speed` | Integer | Initiative | Yes (in params JSONB) |
| `attack` | Integer | Attack rating | Yes (in params JSONB) |
| `defense` | Integer | Defense rating | Yes (in params JSONB) |
| `intellect` | Integer | Intellect/magic power | Yes (in params JSONB) |
| `min_damage` | Integer | Minimum damage | Yes (in params JSONB) |
| `max_damage` | Integer | Maximum damage | Yes (in params JSONB) |
| `features_hints` | String (CSV) | Comma-separated features | Yes (as array in params JSONB) |
| `attacks` | String (CSV) | Comma-separated attack types | Yes (as array in params JSONB) |
| `morale` | Integer | Morale bonus | Yes (in params JSONB) |
| `talents` | Integer | Talent points | Yes (in params JSONB) |
| `priority` | Integer | AI targeting priority | Yes (in params JSONB) |

### Features Hints

The `features_hints` property is a comma-separated list of unit characteristics:

**Common Features**:
- `shooter` - Ranged attacker
- `living` - Living creature (affected by certain spells)
- `undead` - Undead creature (immune to certain effects)
- `male` / `female` - Gender (affects some abilities)
- `large` - Large size (affects positioning)
- `flying` - Can fly over obstacles
- `noans` - No answer/retaliation
- `demon_blood` - Demonic creature
- `mechanical` - Mechanical unit (different resistances)

**Database Storage**: Converted from comma-separated string to array.

**Example**:
- `features_hints=shooter,living,male,noans` → stored as `["shooter", "living", "male", "noans"]`

### Attacks

The `attacks` property is a comma-separated list of attack types:

**Common Attack Types**:
- `melee` - Close combat attack
- `range` - Ranged attack
- `special` - Special ability attack
- `stomp` - Area-of-effect stomp
- `breath` - Breath weapon

**Database Storage**: Converted from comma-separated string to array.

**Example**:
- `attacks=melee,stomp` → stored as `["melee", "stomp"]`

## Unit Class Filtering

### Excluded Unit Types

During extraction, certain unit kb_ids are automatically filtered out:

| Pattern | Reason | Example |
|---------|--------|---------|
| `cpn_hint_*` | Hint/tutorial units | `cpn_hint_bowman` |
| `*_name` | Name-only entries | `bowman_name` |
| `*_spawner` | Spawner entities | `demon_spawner` |
| `class=spirit` | Internal spirit entities | Any unit with spirit class |

### Extraction Rules

1. Query localizations with `tag='units'` and `kb_id` starting with `cpn_`
2. Strip `cpn_` prefix to get unit kb_id
3. Skip if kb_id matches exclusion patterns
4. Parse unit atom file
5. Skip if `main.class == 'spirit'`
6. Raise error if `main` or `arena_params` sections are missing
7. Store in database with all parameters in JSONB

## Localization Integration

### Localization kb_id Pattern

Units have localization strings with this pattern:

```
cpn_<unit_kb_id>
```

**Example**: For unit with kb_id `bowman`:
- Localization entry: `cpn_bowman` = "Лучник" / "Bowman"

**Note**: Unlike items which use `itm_<kb_id>_name`, units use a simpler pattern without suffix.

### Query: Units with Names

```sql
SELECT
    u.kb_id,
    u.unit_class,
    u.params->>'health' as health,
    u.params->>'attack' as attack,
    u.params->>'defense' as defense,
    l.text as name
FROM unit u
LEFT JOIN localization l
    ON l.kb_id = 'cpn_' || u.kb_id
WHERE l.tag = 'units'
ORDER BY u.kb_id;
```

### Query: Units by Race

```sql
SELECT
    u.kb_id,
    u.params->>'race' as race,
    l.text as name,
    u.params->>'level' as level
FROM unit u
LEFT JOIN localization l
    ON l.kb_id = 'cpn_' || u.kb_id
WHERE u.params->>'race' = 'human'
ORDER BY (u.params->>'level')::int;
```

### Query: Units with Specific Feature

```sql
SELECT
    u.kb_id,
    u.params->'features_hints' as features,
    l.text as name
FROM unit u
LEFT JOIN localization l
    ON l.kb_id = 'cpn_' || u.kb_id
WHERE u.params->'features_hints' ? 'shooter'
ORDER BY u.kb_id;
```

## JSONB Parameter Storage

All unit parameters are stored in a flexible JSONB column for several reasons:

1. **Different units have different parameters** - Not all units have the same attributes
2. **Easy extensibility** - New parameters can be added without schema changes
3. **Comma-separated values** - features_hints and attacks are converted to JSON arrays
4. **Nested data preservation** - All sections from atom file are preserved

### Accessing JSONB Data

**Get single value**:
```sql
SELECT params->>'health' FROM unit WHERE kb_id = 'bowman';
```

**Get nested value**:
```sql
SELECT params->'arena_params'->>'attack' FROM unit WHERE kb_id = 'knight';
```

**Get array**:
```sql
SELECT params->'features_hints' FROM unit WHERE kb_id = 'bowman';
-- Returns: ["shooter", "living", "male", "noans"]
```

**Check if array contains value**:
```sql
SELECT * FROM unit WHERE params->'features_hints' ? 'flying';
```

**Filter by numeric value**:
```sql
SELECT * FROM unit WHERE (params->>'health')::int > 100;
```

## Extraction Workflow

1. Query localization table for entries with `tag='units'` and `kb_id LIKE 'cpn_%'`
2. Extract unit kb_ids by stripping `cpn_` prefix
3. Apply filtering rules (skip hints, names, spawners)
4. For each unit kb_id:
   - Locate atom file: `/tmp/<game>/data/<unit_kb_id>.atom`
   - Parse atom file using AtomParser
   - Validate presence of `main` and `arena_params` sections
   - Check if `main.class == 'spirit'` (skip if true)
   - Extract `unit_class` from `main.class`
   - Convert comma-separated fields to arrays:
     - `arena_params.features_hints` → split by comma
     - `arena_params.attacks` → split by comma
   - Store all parameters in JSONB
5. Create Unit entity and save to database
6. Link with localization using `cpn_<kb_id>` pattern

## Usage Examples

### Get All Units with Stats

```sql
SELECT
    u.kb_id,
    l.text as name,
    u.unit_class,
    u.params->>'race' as race,
    u.params->>'level' as level,
    u.params->>'health' as health,
    u.params->>'attack' as attack,
    u.params->>'defense' as defense,
    u.params->>'min_damage' as min_damage,
    u.params->>'max_damage' as max_damage
FROM unit u
LEFT JOIN localization l ON l.kb_id = 'cpn_' || u.kb_id
ORDER BY u.unit_class, (u.params->>'level')::int;
```

### Find Ranged Units

```sql
SELECT
    u.kb_id,
    l.text as name,
    u.params->'attacks' as attack_types
FROM unit u
LEFT JOIN localization l ON l.kb_id = 'cpn_' || u.kb_id
WHERE u.params->'attacks' ? 'range';
```

### Find Flying Units

```sql
SELECT
    u.kb_id,
    l.text as name,
    u.params->>'health' as health
FROM unit u
LEFT JOIN localization l ON l.kb_id = 'cpn_' || u.kb_id
WHERE u.params->'features_hints' ? 'flying'
ORDER BY (u.params->>'health')::int DESC;
```

### Get Strongest Units by Race

```sql
SELECT
    u.params->>'race' as race,
    u.kb_id,
    l.text as name,
    (u.params->>'attack')::int as attack,
    (u.params->>'max_damage')::int as max_damage
FROM unit u
LEFT JOIN localization l ON l.kb_id = 'cpn_' || u.kb_id
WHERE u.params->>'race' = 'demon'
ORDER BY (u.params->>'attack')::int DESC, (u.params->>'max_damage')::int DESC
LIMIT 10;
```

### Find Units by Speed Range

```sql
SELECT
    u.kb_id,
    l.text as name,
    u.params->>'min_speed' as min_speed,
    u.params->>'max_speed' as max_speed,
    u.params->>'speed' as initiative
FROM unit u
LEFT JOIN localization l ON l.kb_id = 'cpn_' || u.kb_id
WHERE (u.params->>'speed')::int >= 4
ORDER BY (u.params->>'speed')::int DESC;
```

### Compare Unit Classes

```sql
SELECT
    u.unit_class,
    COUNT(*) as unit_count,
    AVG((u.params->>'health')::int) as avg_health,
    AVG((u.params->>'attack')::int) as avg_attack,
    AVG((u.params->>'defense')::int) as avg_defense
FROM unit u
GROUP BY u.unit_class;
```

### Get All Unit Features

```sql
SELECT DISTINCT
    jsonb_array_elements_text(u.params->'features_hints') as feature
FROM unit u
ORDER BY feature;
```

### Get All Attack Types

```sql
SELECT DISTINCT
    jsonb_array_elements_text(u.params->'attacks') as attack_type
FROM unit u
ORDER BY attack_type;
```

## Encoding Handling

Unit atom files may use different encodings:

- **UTF-16 LE** - Most common for older files
- **UTF-8** - Common for newer/modded files
- **ISO-8859-1** - Some legacy files

The parser uses `chardet` library for automatic encoding detection with fallback chain. BOM (Byte Order Mark) characters are automatically stripped if present.

## Error Handling

The parser raises specific errors for invalid files:

| Error | Cause |
|-------|-------|
| `ValueError: Unit atom file '<file>' returned empty content` | File exists but is empty or couldn't be decoded |
| `ValueError: Unit '<kb_id>': atom file missing 'main' section` | Atom file lacks main section |
| `ValueError: Unit '<kb_id>': 'main' section is not a dict` | Main section has wrong format |
| `ValueError: Unit '<kb_id>': atom file missing 'arena_params' section` | Atom file lacks arena_params (only for non-spirits) |
| `ValueError: Unit '<kb_id>': 'arena_params' section is not a dict` | Arena_params section has wrong format |

**Note**: Units with `main.class == 'spirit'` return `None` instead of raising errors, as they are valid but filtered entities.
