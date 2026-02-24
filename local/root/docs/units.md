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
| `kb_id` | String (255) | Unique in-game identifier for the unit |
| `name` | String (255) | Localized unit name (fetched from localization with 'cpn_' prefix) |
| `unit_class` | String (50) | Unit classification: "pawn" or "chesspiece" |
| `main` | JSONB | Main section data from atom file |
| `params` | JSONB | Complete arena_params data from atom file |
| `cost` | Integer (nullable) | Unit recruitment cost |
| `krit` | Integer (nullable) | Critical hit chance |
| `race` | String (100, nullable) | Unit race (human, elf, dwarf, demon, etc.) |
| `level` | Integer (nullable) | Unit tier/level |
| `speed` | Integer (nullable) | Initiative/speed rating |
| `attack` | Integer (nullable) | Attack rating |
| `defense` | Integer (nullable) | Defense rating |
| `hitback` | Integer (nullable) | Counterattack capability |
| `hitpoint` | Integer (nullable) | Hit points/health |
| `movetype` | Integer (nullable) | Movement type enum (ON_FOOT=0, SOARING=1, FLIES=2, PHANTOM=-2) |
| `defenseup` | Integer (nullable) | Defense bonus |
| `initiative` | Integer (nullable) | Initiative modifier |
| `leadership` | Integer (nullable) | Leadership cost/requirement |
| `resistance` | JSONB (nullable) | Elemental resistances (physical, magic, fire, etc.) |
| `features` | JSONB (nullable) | Processed features with localized names and hints |
| `attacks` | JSONB (nullable) | Processed special attacks with localized names and hints |

**Note**: All explicit columns (including `name`) are populated during unit scanning by the `UnitFactory`. The `main` and `params` JSONB columns preserve the complete raw data from atom files for reference.

### Unit Class

Units are classified into two types:

| Class | Description |
|-------|-------------|
| `pawn` | Regular combat units that participate in battles |
| `chesspiece` | Special units with unique abilities or roles |

**Note**: Units with `class=spirit` are automatically filtered out during extraction as they are internal game entities not meant for tracking.

### Unit Movetype

Units have different movement types that affect how they traverse the arena:

| Movetype | Value | Description |
|----------|-------|-------------|
| `ON_FOOT` | 0 | Unit moves on foot across the ground |
| `SOARING` | 1 | Unit soars above obstacles |
| `FLIES` | 2 | Unit flies freely |
| `PHANTOM` | -2 | Phantom/incorporeal movement |

**Storage**: Stored as integer in database, converted to `UnitMovetype` enum in application code.

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
| `class` | String | Unit class (pawn, chesspiece, spirit) | Yes (as `unit_class` column) |
| `level` | Integer | Unit tier/level | Yes (explicit column + params JSONB) |
| `race` | String | Unit race (human, elf, dwarf, etc.) | Yes (explicit column + params JSONB) |
| `size` | Integer | Unit size on battlefield | Yes (in params JSONB) |
| `min_speed` | Integer | Minimum initiative | Yes (in params JSONB) |
| `max_speed` | Integer | Maximum initiative | Yes (in params JSONB) |
| `exp_level` | Integer | Experience level | Yes (in params JSONB) |

### Arena Params Section

The `arena_params` section contains combat statistics and abilities:

**Note**: The `movetype` field uses the `UnitMovetype` enum. See the Unit Movetype section for details.

| Property | Type | Description | Stored in DB |
|----------|------|-------------|--------------|
| `cost` | Integer | Recruitment cost | Yes (explicit column + params JSONB) |
| `krit` | Integer | Critical hit chance | Yes (explicit column + params JSONB) |
| `hitpoint` | Integer | Hit points | Yes (explicit column + params JSONB) |
| `speed` | Integer | Initiative | Yes (explicit column + params JSONB) |
| `attack` | Integer | Attack rating | Yes (explicit column + params JSONB) |
| `defense` | Integer | Defense rating | Yes (explicit column + params JSONB) |
| `defenseup` | Integer | Defense bonus | Yes (explicit column + params JSONB) |
| `hitback` | Integer | Counterattack capability | Yes (explicit column + params JSONB) |
| `initiative` | Integer | Initiative modifier | Yes (explicit column + params JSONB) |
| `leadership` | Integer | Leadership cost | Yes (explicit column + params JSONB) |
| `movetype` | Integer | Movement type (see UnitMovetype enum) | Yes (explicit column + params JSONB) |
| `resistances` | Object | Elemental resistances | Yes (as `resistance` column + params JSONB) |
| `features_hints` | String (CSV) | Comma-separated feature kb_ids | Yes (processed in `features` column) |
| `attacks` | String (CSV) | Attack names list | Yes (processed in `attacks` column) |
| `mana` | Integer | Mana points | Yes (in params JSONB) |
| `intellect` | Integer | Intellect/magic power | Yes (in params JSONB) |
| `min_damage` | Integer | Minimum damage | Yes (in params JSONB) |
| `max_damage` | Integer | Maximum damage | Yes (in params JSONB) |
| `morale` | Integer | Morale bonus | Yes (in params JSONB) |
| `talents` | Integer | Talent points | Yes (in params JSONB) |
| `priority` | Integer | AI targeting priority | Yes (in params JSONB) |

**Storage Strategy**: Key combat statistics are stored in explicit columns for efficient querying, while preserving complete raw data in JSONB columns for flexibility.

### Features Processing

The `features_hints` property is a comma-separated list of feature kb_id pairs in the format `header_kb_id/hint_kb_id`:

**Raw Data Example**:
```
features_hints=stamina_header/stamina_3_hint,light_header/light_hint,fur_taker_header/fur_taker_hint
```

**Processing During Scan**:
1. Split comma-separated string into list
2. For each feature kb_id pair:
   - Split by "/" to get `[header_kb_id, hint_kb_id]`
   - Fetch localized name text from `header_kb_id`
   - Fetch localized hint text from `hint_kb_id`
3. Store as JSONB dictionary with full kb_id as key

**Database Storage Format** (`features` column):
```json
{
  "stamina_header/stamina_3_hint": {
    "name": "Stamina",
    "hint": "This unit has 3 health levels"
  },
  "light_header/light_hint": {
    "name": "Light",
    "hint": "Deals extra damage to undead"
  }
}
```

**Fallback**: If localization is missing, the kb_id itself is used as the text.

### Attacks Processing

The `attacks` property references attack definitions stored as dictionaries in `params`. Only **special attacks** (those with a `hint` field) are processed:

**Raw Data Example**:
```
params {
  attacks=moveattack,archdruid_rock,archdruid_stone

  moveattack {
    ad_factor=1
    damage { physical=8,17 }
  }

  archdruid_rock {
    hint=special_archdruid_rocks_hint
    hinthead=special_archdruid_rocks_head
    class=scripted
    reload=3
    # ... attack data ...
  }
}
```

**Processing During Scan**:
1. Iterate through params to find attack dictionaries
2. Filter for attacks containing `hint` field (special attacks only)
3. For each special attack:
   - Fetch localized hint text from `hint` kb_id
   - Derive name kb_id by replacing `_hint` with `_name` in hint kb_id
   - Fetch localized name text (use name kb_id if not found)
4. Store as JSONB dictionary with attack key as key

**Database Storage Format** (`attacks` column):
```json
{
  "archdruid_rock": {
    "name": "Stone Throw",
    "hint": "Throws a rock at the enemy dealing earth damage",
    "data": { /* complete attack dictionary */ }
  },
  "archdruid_stone": {
    "name": "Boulder Smash",
    "hint": "Crushes enemies with a massive boulder",
    "data": { /* complete attack dictionary */ }
  }
}
```

**Note**: Regular attacks like `moveattack` (without `hint` field) are not included in the `attacks` column but remain accessible in the `params` JSONB column.

**Fallback**: If localization is missing, the kb_id itself is used as the text.

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

### Name Storage

Unit names are **stored directly in the `name` column** during entity creation by the `UnitFactory`. The factory fetches the localized name from `LocalizationRepository` using the `cpn_{kb_id}` pattern and stores it in the unit table. This eliminates the need for JOIN queries when retrieving units.

### Query: Units with Names

```sql
SELECT
    u.kb_id,
    u.name,
    u.unit_class,
    u.hitpoint,
    u.attack,
    u.defense
FROM unit u
ORDER BY u.kb_id;
```

**Note**: Unit names are stored directly in the `name` column, so no JOIN with the localization table is required.

### Query: Units by Race

```sql
SELECT
    u.kb_id,
    u.name,
    u.race,
    u.level,
    u.cost
FROM unit u
WHERE u.race = 'human'
ORDER BY u.level;
```

### Query: Units with Specific Feature

```sql
SELECT
    u.kb_id,
    u.name,
    u.features
FROM unit u
WHERE u.features ? 'stamina_header/stamina_3_hint'
ORDER BY u.kb_id;
```

**Note**: The `features` column stores processed features with localized names. To search by feature name text, use:

```sql
SELECT kb_id, features->'stamina_header/stamina_3_hint' as stamina_feature
FROM unit
WHERE features->'stamina_header/stamina_3_hint' IS NOT NULL;
```

## Dual Storage Strategy

Units use a **hybrid storage approach** combining explicit columns with JSONB flexibility:

### Explicit Columns (for Performance)

Key combat statistics are stored as explicit columns for:
- **Fast querying**: Direct column access without JSON extraction
- **Type safety**: Database enforces integer/string types
- **Indexing**: Can create indexes on frequently queried columns
- **Aggregations**: Efficient AVG, SUM, MIN, MAX operations

**Explicit columns**: `cost`, `krit`, `race`, `level`, `speed`, `attack`, `defense`, `hitback`, `hitpoint`, `movetype`, `defenseup`, `initiative`, `leadership`, `resistance`, `features`, `attacks`

### JSONB Columns (for Flexibility)

Complete raw data is preserved in JSONB for:
- **Extensibility**: New parameters added without schema changes
- **Raw data preservation**: Full atom file content accessible
- **Additional properties**: Properties not in explicit columns (e.g., `min_damage`, `max_damage`, `mana`, etc.)
- **Backward compatibility**: Maintains complete historical data

**JSONB columns**: `main`, `params`

### Best Practices

- **Query explicit columns first** for better performance
- **Use JSONB for rare/optional properties** not available as explicit columns
- **Both sources contain same data** for key properties (explicit column values also in JSONB)
- **Explicit columns take precedence** when building Unit entities

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

The extraction process follows a pipeline architecture: **Parser → Factory → Repository**

### Phase 1: Parsing (`KFSUnitParser`)

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
     - `arena_params.features_hints` → split by comma into list
     - `arena_params.attacks` → split by comma into list
   - **Return raw dictionary**: `{kb_id, unit_class, main, params}`
5. Return dictionary of all units: `{kb_id: raw_data, ...}`

### Phase 2: Entity Creation (`UnitFactory`)

6. For each raw unit dictionary:
   - **Fetch unit name** from `ILocalizationRepository`:
     - Lookup localization using `cpn_{kb_id}` pattern
     - Store directly in `name` property (fallback to kb_id if not found)
   - **Extract explicit properties** from `params`:
     - `cost`, `krit`, `race`, `level`, `speed`, `attack`, `defense`
     - `hitback`, `hitpoint`, `movetype`, `defenseup`, `initiative`, `leadership`
     - `resistances` → stored as `resistance`
   - **Process features** (via `UnitFeaturesProcessor`):
     - Parse `params.features_hints` list
     - For each `header_kb_id/hint_kb_id` pair:
       - Fetch localized name and hint from `ILocalizationRepository`
       - Build dictionary: `{full_kb_id: {name, hint}}`
   - **Process special attacks** (via `UnitAttacksProcessor`):
     - Iterate through params to find attack dictionaries
     - Filter for attacks containing `hint` field
     - For each special attack:
       - Fetch localized hint text
       - Derive and fetch localized name text
       - Build dictionary: `{attack_key: {name, hint, data}}`
   - **Create Unit entity** with all properties populated (including name)
   - Return Unit with `id=0` (to be assigned by database)

### Phase 3: Persistence (`UnitRepository`)

7. Batch create all Unit entities in database (with names already populated)
8. Database assigns sequential IDs
9. Unit data ready for querying without requiring localization JOINs

### Architecture Benefits

- **Separation of Concerns**: Parser extracts data, Factory creates entities, Repository handles persistence
- **Type Safety**: All properties explicitly typed on Unit entity
- **Localization**: Features and attacks automatically enriched with translated text
- **Flexibility**: Raw data preserved in JSONB for extensibility
- **Maintainability**: Helper classes (`UnitAttacksProcessor`, `UnitFeaturesProcessor`) keep code modular

## Usage Examples

### Get All Units with Stats

```sql
SELECT
    u.kb_id,
    u.name,
    u.unit_class,
    u.race,
    u.level,
    u.hitpoint,
    u.attack,
    u.defense,
    u.cost,
    u.leadership
FROM unit u
ORDER BY u.unit_class, u.level;
```

**Note**: Uses explicit columns for efficient querying. Additional properties like `min_damage` and `max_damage` remain accessible via `u.params->>'min_damage'`.

### Find Units with Special Attacks

```sql
SELECT
    u.kb_id,
    u.name,
    u.attacks
FROM unit u
WHERE u.attacks IS NOT NULL
ORDER BY jsonb_object_keys(u.attacks);
```

**Query specific attack details**:
```sql
SELECT
    u.kb_id,
    u.name,
    u.attacks->'archdruid_rock'->>'name' as attack_name,
    u.attacks->'archdruid_rock'->>'hint' as attack_hint
FROM unit u
WHERE u.attacks ? 'archdruid_rock';
```

### Find Units with Specific Feature

```sql
SELECT
    u.kb_id,
    u.name,
    u.features->'light_header/light_hint'->>'name' as feature_name,
    u.features->'light_header/light_hint'->>'hint' as feature_hint
FROM unit u
WHERE u.features ? 'light_header/light_hint';
```

### Get Strongest Units by Race

```sql
SELECT
    u.race,
    u.kb_id,
    u.name,
    u.attack,
    u.hitpoint,
    u.cost
FROM unit u
WHERE u.race = 'demon'
ORDER BY u.attack DESC, u.hitpoint DESC
LIMIT 10;
```

### Find Units by Speed Range

```sql
SELECT
    u.kb_id,
    u.name,
    u.speed,
    u.initiative
FROM unit u
WHERE u.speed >= 4
ORDER BY u.speed DESC, u.initiative DESC;
```

### Compare Unit Classes

```sql
SELECT
    u.unit_class,
    COUNT(*) as unit_count,
    ROUND(AVG(u.hitpoint), 2) as avg_health,
    ROUND(AVG(u.attack), 2) as avg_attack,
    ROUND(AVG(u.defense), 2) as avg_defense,
    ROUND(AVG(u.cost), 2) as avg_cost
FROM unit u
WHERE u.hitpoint IS NOT NULL
GROUP BY u.unit_class;
```

### Get All Unit Features (Localized)

```sql
SELECT DISTINCT
    jsonb_object_keys(u.features) as feature_kb_id,
    u.features->jsonb_object_keys(u.features)->>'name' as feature_name
FROM unit u
WHERE u.features IS NOT NULL
ORDER BY feature_name;
```

### Get All Special Attacks (Localized)

```sql
SELECT DISTINCT
    jsonb_object_keys(u.attacks) as attack_key,
    u.attacks->jsonb_object_keys(u.attacks)->>'name' as attack_name
FROM unit u
WHERE u.attacks IS NOT NULL
ORDER BY attack_name;
```

### Query Units by Resistance

```sql
SELECT
    u.kb_id,
    u.name,
    u.resistance->'physical' as physical_resistance,
    u.resistance->'magic' as magic_resistance,
    u.resistance->'fire' as fire_resistance
FROM unit u
WHERE (u.resistance->>'fire')::int > 50
ORDER BY (u.resistance->>'fire')::int DESC;
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
