# Items and Item Sets

## Overview

Items are equipment, artifacts, and consumables that players can acquire and use. Items can belong to item sets, which are collections of related items that provide bonuses when equipped together.

## Database Mapping

### Item Table

**Table**: `item` (in game-specific schema, e.g., `game_19.item`)
**Entity**: `Item`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `kb_id` | String | Unique in-game identifier for the item |
| `price` | Integer | Item price in in-game gold |
| `level` | Integer | Rarity level (1-5, where 1=common, 5=legendary) |
| `propbits` | String[] | Array of item properties (equipment slots, usage types) |
| `item_set_id` | Integer | Foreign key to `item_set` table (nullable) |

### Item Set Table

**Table**: `item_set` (in game-specific schema, e.g., `game_19.item_set`)
**Entity**: `ItemSet`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `kb_id` | String | Unique in-game identifier for the item set |

### Relationship

```
item.item_set_id -> item_set.id
```

An item can optionally belong to a set. Multiple items can reference the same item set.

**Example Data**:

Items:
| id | kb_id | price | level | propbits | item_set_id |
|----|-------|-------|-------|----------|-------------|
| 1 | knight_shield | 34000 | 2 | ["shield"] | 1 |
| 2 | tournament_helm | 91000 | 3 | ["helmet"] | 1 |
| 3 | knightly_boots | 68000 | 3 | ["boots"] | 1 |

Item Sets:
| id | kb_id |
|----|-------|
| 1 | set_knight |
| 2 | set_ogre |
| 3 | set_rage |

## Archive Location

### Location

Items are stored in the main game data archive:

```
/data/<game_name>/sessions/*/ses.kfs
```

**Not** in localization archives (`loc_*.kfs`).

### File Pattern

Inside `ses.kfs`, item definitions are in files matching:

```
item*.txt
```

**Examples**:
- `item.txt`
- `items.txt`
- `items_addon1.txt`
- `items_new.txt`

**Note**: There may be multiple item files per game. All must be parsed to extract complete item data.

## Item File Format

### Syntax Structure

Items use a nested property syntax:

```
item_kb_id {
    property_name=value
    property_name=value

    nested_property {
        key=value
    }

    list_property {
        {
            key1=value1
        }
        {
            key2=value2
        }
    }
}
```

### Example: Simple Item

```
snake_belt {
  category=o
  image=heroitem_belt_snake.png
  hint_config=object_item
  label=itm_snake_belt_name
  hint=itm_snake_belt_hint
  information_label=itm_snake_belt_info
  maphint=
  mapinfo=
  atoms {
    1 {
      atom=
      lu=template_item_mb
      label=
    }
  }
  price=15000
  maxcount=2
  level=2
  race=neutral
  setref=set_neutral_snake_sorcerer
  use { }
  fight {
    {
      filter {
        belligerent=ally
        unit=snake,snake_green,snake_royal
      }
      pbonus=health,0,10,0,-100,0,0
      dbonus=
      rbonus=
      attack_on=
      attack_off=
    }
  }
  mods {
    mana=limit,5
    sp_hero_penalty_chance_poison=count,5
  }
  propbits=belt
  params {
    count1=0
  }
  actions { }
}
```

### Example: Item with Army

```
shield {
  category=o
  image=heroitem_shield_02.png
  hint_config=object_item
  label=itm_shield_name
  hint=itm_shield_hint
  information_label=itm_shield_info
  maphint=
  mapinfo=
  atoms {
    1 {
      atom=
      lu=template_item_mb
      label=
    }
  }
  price=7000
  maxcount=2
  level=1
  race=viking
  use {
    upgrade=barbarian_shield
  }
  mods {
    defense=count,1
  }
  propbits=shield
  arena=aitem_viking_01
  army {
    name=
    jnt=0
    tdf=1
    choice {
      {
        name=Troop variant #0
        prob=100
        hero=0
        bod=1
        lead1=1000
        lead2=1000
        script=
        disp=1
        arra=1
        beh=Aggression
        troops {
          {
            races=viking
            units=
            level=1:3
            perc=10:30
            kolvo=0
            prob=100
            ext=-1
            fillt=2
          }
        }
      }
    }
    chance=100
    class=army
  }
  params {
    upgrade=shield,barbarian_shield
  }
  actions { }
}
```

## Properties of Interest

### Core Properties

| Property | Type | Description | Stored in DB |
|----------|------|-------------|--------------|
| `price` | Integer | Item price in gold | Yes |
| `level` | Integer | Rarity (1-5) | Yes |
| `propbits` | String | Item type/slot | Yes (as array) |
| `setref` | String | Reference to item set kb_id | Yes (via item_set_id) |

### propbits Property

**Format**: String value indicating how the item can be used.

**Common Values**:
- Equipment slots: `helmet`, `armor`, `boots`, `shield`, `belt`, `amulet`, `ring`, `weapon`, `regalia`
- Special: `book`, `scroll`, `medal`, `usable`, `consumable`

**Database Storage**: Converted to array of strings.

**Examples**:
- `propbits=shield` → stored as `["shield"]`
- `propbits=ring` → stored as `["ring"]`
- Item can have multiple propbits (fits multiple slots)

### setref Property

**Purpose**: Links item to an item set.

**Format**: String containing item set kb_id.

**Example**:
```
setref=set_neutral_snake_sorcerer
```

**Database Handling**:
1. Parse `setref` value
2. Find or create item_set record with matching kb_id
3. Set item.item_set_id to reference that item_set

### Other Properties

Properties **not** currently stored in database:
- `category` - Item category
- `image` - Image file path
- `race` - Associated race
- `mods` - Stat modifications
- `use` - Usage effects
- `fight` - Combat bonuses
- `army` - Army encounter data
- `actions` - Binary serialized data (not parseable)
- `params` - Various parameters

These are preserved in original game files but not extracted to database.

## Item Sets

### Definition in Resource Files

Item sets are defined via the `setref` property in item definitions.

**Example Items in Same Set**:

```
knight_shield {
  ...
  setref=set_knight
  ...
}

tournament_helm {
  ...
  setref=set_knight
  ...
}

knightly_boots {
  ...
  setref=set_knight
  ...
}
```

All three items belong to `set_knight`.

### Database Relationship

**Extraction Process**:
1. Parse item file
2. Extract `setref` value (e.g., `set_knight`)
3. Look up or create `item_set` record with `kb_id = 'set_knight'`
4. Set `item.item_set_id` to the `item_set.id`

**Query Example**: Find all items in a set:

```sql
SELECT i.*
FROM item i
JOIN item_set s ON i.item_set_id = s.id
WHERE s.kb_id = 'set_knight';
```

**Query Example**: Find items with their set names:

```sql
SELECT
    i.kb_id,
    i.price,
    i.level,
    s.kb_id as set_name
FROM item i
LEFT JOIN item_set s ON i.item_set_id = s.id
WHERE i.item_set_id IS NOT NULL;
```

## Localization Integration

### Localization kb_id Pattern

Items have localization strings with this pattern:

```
itm_<item_kb_id>_<kind>
```

**Localization Kinds** for items:
- `name` - Item display name
- `hint` - Mouse-over hint (stats, effects, bonuses)
- `info` - Item lore/description
- `taken` - Text when acquired
- `minfo` - Map info
- `mhint` - Map hint

**Example**: For item with kb_id `shield`:
- `itm_shield_name` - "Щит" / "Shield"
- `itm_shield_hint` - "+1 Защиты" / "+1 Defense"
- `itm_shield_info` - Lore text

### Query: Items with Names

```sql
SELECT
    i.kb_id,
    i.price,
    i.level,
    i.propbits,
    l.text as name
FROM item i
LEFT JOIN localization l
    ON l.kb_id = 'itm_' || i.kb_id || '_name'
ORDER BY i.price DESC
LIMIT 20;
```

### Query: Items with Names and Hints

```sql
SELECT
    i.kb_id,
    i.price,
    i.level,
    name_loc.text as name,
    hint_loc.text as hint
FROM item i
LEFT JOIN localization name_loc
    ON name_loc.kb_id = 'itm_' || i.kb_id || '_name'
LEFT JOIN localization hint_loc
    ON hint_loc.kb_id = 'itm_' || i.kb_id || '_hint'
ORDER BY i.level DESC, i.price DESC
LIMIT 10;
```

### Query: Item Sets with Localization

Item sets also have localization strings:

**Pattern**: `set_<item_set_kb_id>_<kind>`

**Example**:

```sql
SELECT
    s.kb_id,
    l.text as set_name,
    COUNT(i.id) as item_count
FROM item_set s
LEFT JOIN localization l
    ON l.kb_id = 'set_' || s.kb_id || '_name'
LEFT JOIN item i
    ON i.item_set_id = s.id
GROUP BY s.kb_id, l.text;
```

## Rarity Levels

The `level` property indicates item rarity:

| Level | Rarity |
|-------|--------|
| 1 | Common |
| 2 | Uncommon |
| 3 | Rare |
| 4 | Epic |
| 5 | Legendary |

**Query Example**: Get legendary items:

```sql
SELECT
    i.kb_id,
    i.price,
    l.text as name
FROM item i
LEFT JOIN localization l
    ON l.kb_id = 'itm_' || i.kb_id || '_name'
WHERE i.level = 5
ORDER BY i.price DESC;
```

## Extraction Workflow

1. Locate game data archive: `/data/<game>/sessions/*/ses.kfs`
2. Extract archive (it's a ZIP file)
3. Find all `item*.txt` files
4. Parse each file:
   - Extract item blocks (item_kb_id { ... })
   - Parse properties: price, level, propbits, setref
   - Handle item sets (create/lookup item_set records)
5. Store in database:
   - Insert/update `item_set` records
   - Insert/update `item` records with proper foreign keys
6. Link with localization using kb_id patterns

## Usage Examples

### Find Item by Name

```sql
SELECT i.*
FROM item i
JOIN localization l
    ON l.kb_id = 'itm_' || i.kb_id || '_name'
WHERE l.text ILIKE '%shield%';
```

### Get Expensive Items

```sql
SELECT
    i.kb_id,
    i.price,
    i.level,
    l.text as name
FROM item i
LEFT JOIN localization l
    ON l.kb_id = 'itm_' || i.kb_id || '_name'
WHERE i.price > 50000
ORDER BY i.price DESC;
```

### Find Items by Equipment Slot

```sql
SELECT
    i.kb_id,
    i.propbits,
    l.text as name
FROM item i
LEFT JOIN localization l
    ON l.kb_id = 'itm_' || i.kb_id || '_name'
WHERE 'helmet' = ANY(i.propbits);
```

### Get Complete Set Information

```sql
SELECT
    s.kb_id as set_kb_id,
    set_loc.text as set_name,
    i.kb_id as item_kb_id,
    item_loc.text as item_name,
    i.price,
    i.level
FROM item_set s
LEFT JOIN localization set_loc
    ON set_loc.kb_id = 'set_' || s.kb_id || '_name'
JOIN item i
    ON i.item_set_id = s.id
LEFT JOIN localization item_loc
    ON item_loc.kb_id = 'itm_' || i.kb_id || '_name'
WHERE s.kb_id = 'set_knight'
ORDER BY i.level DESC, i.price DESC;
```
