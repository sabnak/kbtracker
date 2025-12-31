# Localization Resources

## Overview

Localization resources contain translated text for all game entities across multiple languages. Each language string has a unique kb_id that links it to specific game entities (items, spells, units, quests, etc.).

## Database Mapping

### Table Structure

**Table**: `localization` (in game-specific schema, e.g., `game_19.localization`)
**Entity**: `Localization`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `kb_id` | String | Unique in-game identifier for the language string |
| `text` | Text | Localized text content (may contain BBCode/HTML tags) |
| `source` | String | Source file name (without extension) for debugging |
| `tag` | String | Artificial tag for debugging (usually equals source) |

**Note**: `source` and `tag` columns are for debugging purposes and are not used in application logic.

## Archive Location

### Location Pattern

Localization archives are located in:

```
/data/<game_name>/sessions/*/loc_*.kfs
```

### Archive Naming

Archives follow the pattern: `loc_<identifier>.kfs`

**Examples** (King's Bounty: Dark Side):
- `loc_ses.kfs` - Russian localization
- `loc_ses_eng.kfs` - English localization
- `loc_ses_ger.kfs` - German localization
- `loc_ses_pol.kfs` - Polish localization

**Important Notes**:
- Archive names vary by game version
- Not all games support the same languages
- All games support at least Russian
- Community mods may have their own localization archives

### Directory Structure

```
/data/Darkside/sessions/
├── base/              (may contain loc_*.kfs)
└── darkside/          (main session)
    ├── loc_ses.kfs
    ├── loc_ses_eng.kfs
    ├── loc_ses_ger.kfs
    ├── loc_ses_pol.kfs
    └── ses.kfs
```

## Language File Format

### File Naming Pattern

Inside loc_*.kfs archives, language files follow this pattern:

```
<lng>_<name>.lng
```

**Components**:
- `<lng>`: Three-letter lowercase language code
- `<name>`: Resource category name
- Extension: `.lng` (plain text)

**Examples**:
- `rus_items.lng` - Russian item texts
- `eng_spells.lng` - English spell texts
- `ger_units.lng` - German unit texts
- `pol_quests.lng` - Polish quest texts

**Language Codes**:
- `rus` - Russian
- `eng` - English
- `ger` - German
- `pol` - Polish

### File Content Format

**Format**: Strict key-value pairs, one per line

```
<kb_id>=<text>
```

**Rules**:
- Each language entry on a new line
- No multiline entries
- Text may contain BBCode tags: `[s]`, `[/s]`, `[d]`, `[sys]`
- Text may contain HTML tags: `<br>`, `<label=...>`
- Special characters: `^?^` (purpose varies by context)

### Example Content

From `rus_items.lng`:

```
itm_addon4_dwarf_giant_boots_name=Сабатоны Гиганта
itm_addon4_dwarf_giant_boots_taken=^?^
itm_addon4_dwarf_giant_boots_minfo=^?^
itm_addon4_dwarf_giant_boots_mhint=^?^
itm_addon4_dwarf_giant_boots_info=^?^Наследие древних веков...
itm_addon4_dwarf_giant_boots_hint=^?^Некоторые существа могли бы...<br>[s]+3 Защиты[/s]
```

From `eng_spells.lng`:

```
spell_dispell_name=Dispel
SN_dispell=^spells_tN^
spell_dispell_header=^spells_tC^
spell_dispell_desc_1=^spells_tSpell^Removes all effects from a friendly target.<br>The following effects are not removed: <label=effect_freeze_name>
```

## Localization kb_id Patterns

### Structure

Localization kb_id follows entity-specific patterns:

```
<prefix>_<entity_kb_id>_<kind>
```

**Components**:
- `<prefix>`: Entity type prefix (e.g., `itm`, `spell`)
- `<entity_kb_id>`: The entity's kb_id
- `<kind>`: String type (name, hint, info, etc.)

### Items Pattern

**Pattern**: `itm_<item_kb_id>_<kind>`

**Kinds** (string types for items):
- `name` - Item name (display name)
- `hint` - Mouse-over hint (game stats, effects)
- `info` - Item lore (background story)
- `taken` - Text when item acquired
- `minfo` - Map info
- `mhint` - Map hint

**Example**: For item with kb_id `shield`:
- `itm_shield_name` - "Щит" (Russian) / "Shield" (English)
- `itm_shield_hint` - Game stats and effects
- `itm_shield_info` - Item description/lore

### Other Entity Patterns

While items use `itm_` prefix, other entities have their own:
- Spells: `spell_<spell_kb_id>_<kind>`
- Units: Variable patterns based on game version
- Quests: Variable patterns based on game version

## Querying Localization

### Finding Localization for Specific Entity

To find all localization strings for an item with kb_id `addon4_orc_battle_hoe_2`:

```sql
SELECT *
FROM localization
WHERE kb_id LIKE 'itm_addon4_orc_battle_hoe_2%'
ORDER BY kb_id;
```

**Result**:

| id | kb_id | text | source | tag |
|----|-------|------|--------|-----|
| 7000 | itm_addon4_orc_battle_hoe_2_name | Кромсатор | items | items |
| 7001 | itm_addon4_orc_battle_hoe_2_taken | ^?^ | items | items |
| 7002 | itm_addon4_orc_battle_hoe_2_minfo | ^?^ | items | items |
| 7003 | itm_addon4_orc_battle_hoe_2_mhint | ^?^ | items | items |
| 7004 | itm_addon4_orc_battle_hoe_2_info | ^?^Жутковатое нагромождение... | items | items |
| 7005 | itm_addon4_orc_battle_hoe_2_hint | ^?^Лишь при одном взгляде...<br>[s]+6 Атаки[/s] | items | items |

### Getting Specific Localization Kind

To get only item names:

```sql
SELECT kb_id, text
FROM localization
WHERE kb_id LIKE 'itm_%_name'
LIMIT 10;
```

To get item hints (game stats):

```sql
SELECT kb_id, text
FROM localization
WHERE kb_id LIKE 'itm_%_hint'
LIMIT 10;
```

### Joining with Entity Tables

Example: Get items with their localized names:

```sql
SELECT
    i.kb_id,
    i.price,
    i.level,
    l.text as name
FROM item i
LEFT JOIN localization l
    ON l.kb_id = 'itm_' || i.kb_id || '_name'
LIMIT 10;
```

## BBCode and HTML Tags

Localized text may contain formatting tags:

### BBCode Tags

- `[s]...[/s]` - Styling/highlighting
- `[d]` - Delimiter or special formatting
- `[sys]...[/sys]` - System text
- `[medal]` - Medal indicator

### HTML Tags

- `<br>` - Line break
- `<label=kb_id>` - Reference to another localization string

**Example**:

```
text=Removes all effects.<br>The following are not removed: <label=effect_freeze_name>
```

This references another localization entry with kb_id `effect_freeze_name`.

## Special Markers

### ^?^ Marker

The `^?^` marker appears at the beginning of many localization strings. Its exact purpose varies by context, but it's part of the original game format.

**Examples**:
- `^?^` - Empty or placeholder
- `^?^Item description text` - Precedes actual content
- `^spells_tN^` - Template reference

## Extraction Workflow

1. Locate localization archive: `/data/<game>/sessions/*/loc_*.kfs`
2. Extract archive (it's a ZIP file)
3. Locate language files: `<lng>_*.lng`
4. Parse each line as `kb_id=text` pairs
5. Store in `localization` table
6. Link to entities using kb_id patterns

## Usage Examples

### Find Item Description

```sql
SELECT text
FROM localization
WHERE kb_id = 'itm_shield_info';
```

### Find All Russian Item Names

```sql
SELECT kb_id, text
FROM localization
WHERE kb_id LIKE 'itm_%_name'
AND source = 'items';
```

### Search for Text Content

```sql
SELECT kb_id, text
FROM localization
WHERE text ILIKE '%dragon%'
LIMIT 20;
```
