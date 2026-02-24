# Spells

## Overview

Spells are magical abilities that can be cast in combat or on the adventure map. There are two main categories: battle spells (cast during combat with upgrade levels) and wandering spells (cast on the adventure map without levels).

## Database Mapping

### Table Structure

**Table**: `spell` (in game-specific schema, e.g., `game_19.spell`)
**Entity**: `Spell`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `kb_id` | String | Unique in-game identifier for the spell |
| `profit` | Integer | Spell value/profit metric |
| `price` | Integer | Spell price in in-game gold |
| `school` | Integer | Magic school (1-5, see SpellSchool enum) |
| `mana_cost` | Integer[] | Array of mana costs per level (NULL for wandering spells) |
| `crystal_cost` | Integer[] | Array of crystal costs per level (NULL for wandering spells) |
| `data` | JSONB | Complete spell configuration (scripted blocks, params, raw data) |

**Note**: `loc` field is NOT stored in the database. Localization is fetched dynamically using LocStrings pattern (see [localization.md](localization.md#locstrings-pattern)).

## Spell Schools

Spells are categorized into five magic schools:

| School ID | School Name | Type | Description |
|-----------|-------------|------|-------------|
| 1 | ORDER | Battle | Order magic (healing, buffs, protection) |
| 2 | CHAOS | Battle | Chaos magic (damage, debuffs) |
| 3 | DISTORTION | Battle | Distortion magic (manipulation, control) |
| 4 | MIND | Battle | Mind magic (mental effects, illusions) |
| 5 | WANDERING | Adventure | Adventure map spells (no combat use) |

**Battle Spells** (schools 1-4):
- Have upgrade levels (typically 3 levels)
- Have mana_cost and crystal_cost arrays
- Cast during combat

**Wandering Spells** (school 5):
- No upgrade levels
- mana_cost and crystal_cost are NULL
- Cast on adventure map

## Archive Location

### Location

Spells are stored in the main game data archive:

```
/data/<game_name>/sessions/*/ses.kfs
```

**Not** in localization archives (`loc_*.kfs`).

### File Pattern

Inside `ses.kfs`, spell definitions are in files matching:

```
spells*.txt
```

**Files**:
- `spells.txt` - Battle spells (schools 1-4)
- `spells_adventure.txt` - Wandering spells (school 5)

**Important**: Both files must be parsed to extract complete spell data.

## Spell File Format

### Syntax Structure

Spells use atom file format (see [atom-parser.md](atom-parser.md)):

```
spell_kb_id {
    profit=1
    price=2000
    school=1

    levels {
        {
            manacost=5
            crystal=1
        }
        {
            manacost=5
            crystal=2
        }
        {
            manacost=5
            crystal=5
        }
    }

    scripted {
        no_hint=1
        script_attack=spell_kb_id_attack
    }

    params {
        duration=0
        target=ally,all,all
    }
}
```

### Example: Battle Spell (with levels)

From `spells.txt`:

```
dispell {
  profit=1
  price=2000
  school=1

  levels {
    {
      manacost=5
      crystal=1
    }
    {
      manacost=5
      crystal=2
    }
    {
      manacost=5
      crystal=5
    }
  }

  scripted {
    no_hint=1
    script_attack=spell_dispell_attack
    script_calccells=calccells_spell_dispell
    attack_cursor=magicstick
    ad_factor=0
    nfeatures=magic_immunitet,pawn,boss
  }

  params {
    duration=0
    type=bonus
    exception=effect_burn,effect_freeze,effect_poison,effect_bleed
    target=ally,all,all
    ally_dispell=all,all,penalty
    enemy_dispell=none,all,bonus
  }
}
```

**Stored Data** (after parsing):

```json
{
  "kb_id": "dispell",
  "profit": 1,
  "price": 2000,
  "school": 1,
  "mana_cost": [5, 5, 5],
  "crystal_cost": [1, 2, 5],
  "data": {
    "scripted": {
      "no_hint": 1,
      "script_attack": "spell_dispell_attack",
      "script_calccells": "calccells_spell_dispell",
      "attack_cursor": "magicstick",
      "ad_factor": 0,
      "nfeatures": ["magic_immunitet", "pawn", "boss"]
    },
    "params": {
      "duration": 0,
      "type": "bonus",
      "exception": ["effect_burn", "effect_freeze", "effect_poison", "effect_bleed"],
      "target": ["ally", "all", "all"],
      "ally_dispell": ["all", "all", "penalty"],
      "enemy_dispell": ["none", "all", "bonus"]
    }
  }
}
```

### Example: Wandering Spell (no levels)

From `spells_adventure.txt`:

```
titan_sword {
  profit=4
  price=50000
  school=5

  action=advspell_titan_sword
  category=s
  image=book_spell_titan_sword.png
  label=spell_titan_sword_name
  hint=spell_titan_sword_hint
}
```

**Stored Data** (after parsing):

```json
{
  "kb_id": "titan_sword",
  "profit": 4,
  "price": 50000,
  "school": 5,
  "mana_cost": null,
  "crystal_cost": null,
  "data": {
    "action": "advspell_titan_sword",
    "category": "s",
    "image": "book_spell_titan_sword.png",
    "label": "spell_titan_sword_name",
    "hint": "spell_titan_sword_hint"
  }
}
```

## Spell Data Structure

### Common Fields

All spells have these fields:

- `kb_id` - Unique identifier
- `profit` - Value metric (1-4, higher = better)
- `price` - Purchase price in gold
- `school` - Magic school (1-5)
- `data` - Complete configuration in JSONB

### Level-Specific Fields

**Battle spells** have:
- `mana_cost` - Array of mana costs per level (e.g., `[5, 5, 5]`)
- `crystal_cost` - Array of crystal costs per level (e.g., `[1, 2, 5]`)

**Wandering spells** have:
- `mana_cost` - NULL
- `crystal_cost` - NULL

### Data JSONB Field

The `data` column contains all spell configuration:

**For battle spells**:
```json
{
  "scripted": {
    "no_hint": 1,
    "script_attack": "spell_name_attack",
    "script_calccells": "calccells_spell_name",
    "attack_cursor": "cursor_name",
    "ad_factor": 0,
    "nfeatures": ["feature1", "feature2"]
  },
  "params": {
    "duration": 0,
    "type": "bonus",
    "target": ["ally", "all", "all"],
    "exception": ["effect1", "effect2"]
  },
  "raw": {
    "category": "s",
    "image": "book_spell_name.png",
    "button_image": "book_scroll_name.png"
  }
}
```

**For wandering spells**:
```json
{
  "action": "advspell_name",
  "category": "s",
  "image": "book_spell_name.png",
  "label": "spell_name_name",
  "hint": "spell_name_hint"
}
```

## Localization Integration

### Pattern

Spells use the LocStrings pattern for localization (see [localization.md](localization.md#locstrings-pattern)).

**Localization kb_id pattern**: `spell_<spell_kb_id>_<suffix>`

### Standard Suffixes

| Suffix | Field | Example |
|--------|-------|---------|
| `_name` | Display name | `spell_dispell_name=Dispel` |
| `_hint` | Short description | `spell_dispell_hint=Removes all effects` |
| `_desc` | Full description | `spell_dispell_desc=This spell removes...` |
| `_header` | School/category | `spell_dispell_header=Order Magic` |

### Fetching Pattern

When retrieving a spell from the repository, localizations are fetched using regex pattern:

```regex
^spell_{kb_id}(?:_|$)
```

**Example**: For spell `dispell`, fetch all localizations matching `spell_dispell_*` or exactly `spell_dispell`.

**Important**: The pattern uses regex to avoid matching similar spell names (e.g., `empathy` should not match `empathy2`).

### LocStrings Result

```python
Spell(
    id=1,
    kb_id='dispell',
    profit=1,
    price=2000,
    school=SpellSchool.ORDER,
    mana_cost=[5, 5, 5],
    crystal_cost=[1, 2, 5],
    data={...},
    loc=LocStrings(
        name='Dispel',
        hint='Removes all effects from target unit',
        desc='This spell removes all magical effects',
        header='Order Magic',
        texts={
            'spell_dispell_name': 'Dispel',
            'spell_dispell_hint': 'Removes all effects from target unit',
            'spell_dispell_desc': 'This spell removes all magical effects',
            'spell_dispell_header': 'Order Magic'
        }
    )
)
```

## Querying Spells

### Get All Spells

```sql
SELECT *
FROM spell
ORDER BY school, kb_id;
```

### Get Spells by School

```sql
-- Battle spells only (schools 1-4)
SELECT *
FROM spell
WHERE school BETWEEN 1 AND 4
ORDER BY school, kb_id;

-- Wandering spells only (school 5)
SELECT *
FROM spell
WHERE school = 5
ORDER BY kb_id;
```

### Get Spell with Localization

```sql
SELECT
    s.kb_id,
    s.profit,
    s.price,
    s.school,
    s.mana_cost,
    s.crystal_cost,
    l_name.text as name,
    l_hint.text as hint
FROM spell s
LEFT JOIN localization l_name
    ON l_name.kb_id = 'spell_' || s.kb_id || '_name'
LEFT JOIN localization l_hint
    ON l_hint.kb_id = 'spell_' || s.kb_id || '_hint'
WHERE s.school = 1
ORDER BY s.kb_id;
```

### Search by Name

```sql
SELECT
    s.kb_id,
    s.school,
    s.price,
    l.text as name
FROM spell s
JOIN localization l
    ON l.kb_id = 'spell_' || s.kb_id || '_name'
WHERE l.text ILIKE '%fire%'
ORDER BY s.school, s.kb_id;
```

### Query JSONB Data

```sql
-- Find spells with specific target
SELECT kb_id, data->'params'->>'target' as target
FROM spell
WHERE data->'params'->>'target' LIKE '%ally%';

-- Find spells with script_attack
SELECT kb_id, data->'scripted'->>'script_attack' as attack_script
FROM spell
WHERE data->'scripted' ? 'script_attack';

-- Find wandering spells with specific action
SELECT kb_id, data->>'action' as action
FROM spell
WHERE school = 5
  AND data->>'action' = 'advspell_titan_sword';
```

## Parsing Workflow

1. Extract `ses.kfs` archive from game directory
2. Locate spell files: `spells.txt` and `spells_adventure.txt`
3. Parse using atom parser (see [atom-parser.md](atom-parser.md))
4. Extract spell data:
   - For battle spells: Extract `levels` block → convert to mana_cost/crystal_cost arrays
   - For wandering spells: Set mana_cost/crystal_cost to NULL
   - Split comma-separated params fields to arrays
5. Store in `spell` table (without loc field)
6. On retrieval: Fetch localizations and populate LocStrings dynamically

## Example Queries

### Get Expensive Battle Spells

```sql
SELECT
    s.kb_id,
    s.school,
    s.price,
    l.text as name
FROM spell s
JOIN localization l ON l.kb_id = 'spell_' || s.kb_id || '_name'
WHERE s.school BETWEEN 1 AND 4
  AND s.price > 10000
ORDER BY s.price DESC;
```

### Get Spells by Mana Cost

```sql
-- Spells with first level mana cost = 5
SELECT
    kb_id,
    mana_cost[1] as level_1_mana,
    crystal_cost[1] as level_1_crystal
FROM spell
WHERE mana_cost[1] = 5
ORDER BY crystal_cost[1];
```

### Count Spells by School

```sql
SELECT
    school,
    COUNT(*) as spell_count
FROM spell
GROUP BY school
ORDER BY school;
```

## Special Considerations

### Comma-Separated Fields

Some params fields contain comma-separated values that are split into arrays during parsing:

**Original**:
```
target=ally,all,all
exception=effect_burn,effect_freeze,effect_poison
```

**After parsing**:
```json
{
  "params": {
    "target": ["ally", "all", "all"],
    "exception": ["effect_burn", "effect_freeze", "effect_poison"]
  }
}
```

### Similar Spell Names

When fetching localizations, the regex pattern `^spell_{kb_id}(?:_|$)` prevents matching similar names:

- Fetching `empathy` will NOT match `empathy2` localizations
- The pattern requires either underscore or end-of-string after kb_id

### No Redundant Storage

Unlike some entity types, spells do NOT store localization in the database table. The `loc` field is populated dynamically by the repository using the LocStrings pattern, eliminating data duplication.
