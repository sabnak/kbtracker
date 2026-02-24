# Shop Parsing Investigation - 2026-01-16

## Executive Summary

**Finding:** The shop is missing because it uses an **`NPC_template@` marker** instead of `building_trader@` or standalone `itext_` identifier.

**Root Cause:** The ShopInventoryParser only recognizes two patterns:
1. `itext_{location}_{number}` (without `_hint` or `_msg` suffix)
2. `building_trader@{num}`

**Impact:** Approximately **45 shops with inventory (~11-12% of total)** are missing from parser output due to `NPC_template@` pattern not being supported.

**Shop Location:** Position 113231 in decompressed save data
- Has all expected inventory (items, units, spells)
- Uses `NPC_template@915` marker
- Has localization labels `itext_m_inselburg_6529_hint` and `itext_m_inselburg_6529_msg` (not standalone `itext_m_inselburg_6529`)

---

## Problem Statement

The save file at `/tests/game_files/saves/quick1768586988` is missing a shop when parsed with the ShopInventoryParser.

**Expected Shop Details:**
- Location: m_inselburg
- itext: m_inselburg_6529
- Expected Inventory:
  - Items: addon2_belt_obeliks_belt, astral_bow
  - Units: pirat2 x2580, robber x2140, assassin x300, spider_venom x9000, spider_fire x9200
  - Spells: fire_arrow x3, advspell_summon_bandit x1, titan_sword x1

## Investigation Steps

### 1. Documentation Review
- [x] Review `/docs/save-extractor` for save format specifications
- [x] Check recent research in `/tests/research/save_decompiler/kb_shop_extractor/`
- [x] Review parser source code

### 2. Save File Analysis
- [x] Run parser: `s /app/tests/game_files/saves/quick1768586988`
- [x] Examine raw decompiled data
- [x] Compare against parser output

### 3. Root Cause Analysis
- [x] Identify why shop is missing
- [x] Document specific parsing issues
- [x] Count total NPC_template@ occurrences
- [x] Estimate impact on parser coverage

## Findings

### Documentation Review

Reviewed `/docs/save-extractor/README.md`:
- Parser version 1.4.0 supports three shop types:
  - itext only: `{location}_{shop_num}` (e.g., `m_portland_8671`)
  - Actor only: `{location}_actor_{actor_id}` (e.g., `dragondor_actor_807991996`)
  - Both itext and actor: Merged when shop has both identifiers
- Recent fix (v1.4.0) handles building_trader@ shops with actor ID extraction
- Previous investigation (2026-01-15) found similar issue with m_portland_dark_6533

### Save File Parsing Results

Executed: `s /app/tests/game_files/saves/quick1768586988`

**Results:**
- Total shops extracted: 357
- m_inselburg shops found: m_inselburg_6557, m_inselburg_6575, m_inselburg_6578, m_inselburg_6582, m_inselburg_6507, m_inselburg_3626, m_inselburg_4111, m_inselburg_6535
- **m_inselburg_6529: NOT FOUND**

The shop identifier `itext_m_inselburg_6529` is missing from the parsed output despite being expected.

### Raw Data Examination

Decompressed save file to `/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/decompressed_data.bin`.

**Search Results:**

1. `itext_m_inselburg_6529` FOUND at 4 positions: 113773, 113875, 7757345, 7757447
   - BUT: These are NOT shop identifiers - they are localization label references
   - Found as: `itext_m_inselburg_6529_hint` and `itext_m_inselburg_6529_msg`

2. Expected inventory FOUND at position 113231 (0x1ba4f):
   - pirat2/2580
   - robber/2140
   - assassin/300
   - spider_venom/9000
   - spider_fire/9200
   - Items: addon2_belt_obeliks_belt, astral_bow
   - Spells: spell_advspell_summon_bandit, spell_fire_arrow, spell_titan_sword

**Shop Structure at Position 113231:**

```
Position 112893: .items section
  - addon2_belt_obeliks_belt (slot 0, quantity 1)
  - astral_bow (slot 1, quantity 1)

Position 113184: .shopunits section
  - pirat2/2580/robber/2140/assassin/300/spider_venom/9000/spider_fire/9200

Position 113310: .spells section
  - spell_advspell_summon_bandit x1
  - spell_fire_arrow x3
  - spell_titan_sword x1

Position 113497: .temp section

Position 113773: itext_m_inselburg_6529_hint (localization label - NOT a shop ID)
Position 113875: itext_m_inselburg_6529_msg (localization label - NOT a shop ID)
```

### Critical Finding: Missing Shop Identifier Pattern

**The Problem:** The shop inventory data exists in the save file, but there is NO shop identifier in the format that the parser expects!

The parser searches for:
1. Pattern 1 (itext): `itext_{location}_{number}` (just the number, no suffix)
2. Pattern 2 (building_trader): `building_trader@{num}` followed by location name

What we found:
- `itext_m_inselburg_6529_hint` (label reference, not shop ID)
- `itext_m_inselburg_6529_msg` (label reference, not shop ID)
- NO standalone `itext_m_inselburg_6529` identifier
- NO `building_trader@` pattern near this shop data

### Further Investigation: NPC Template Shop

Searched for shop markers around the inventory position (113231):

**Backwards search (111231-113231):**
- NO `building_trader@` found
- Multiple `NPC_template@` markers found with m_inselburg location
- `.actors` section at position 111477 with strg value 0x04000000
  - Bit 7 NOT set, indicating inactive/template shop (according to current parser logic)

**Forward search (from .temp at 113497):**
- Position 114084: `lt` tag with value `m_inselburg`
- Position 114095: **`NPC_template@915`** (NOT `building_trader@`)

**Complete shop structure:**
```
Position 111477: .actors (strg: 0x04000000, bit 7 not set)
Position 112893: .items (addon2_belt_obeliks_belt, astral_bow)
Position 113184: .shopunits (pirat2/2580/robber/2140/assassin/300/spider_venom/9000/spider_fire/9200)
Position 113310: .spells (spell_advspell_summon_bandit x1, spell_fire_arrow x3, spell_titan_sword x1)
Position 113497: .temp
Position 113773: itext_m_inselburg_6529_hint (localization label)
Position 113875: itext_m_inselburg_6529_msg (localization label)
Position 114084: lt m_inselburg
Position 114095: NPC_template@915
```

## Root Cause Analysis

### Parser Architecture

Reviewed `/app/src/utils/parsers/save_data/ShopInventoryParser.py`:

The parser has two search patterns:
1. `_find_all_shop_ids()` - searches for `itext_{location}_{number}` (UTF-16 LE)
2. `_find_building_trader_shops()` - searches for `building_trader@{num}` (ASCII)

**Critical limitation:** The parser DOES NOT search for `NPC_template@` markers.

### Why This Shop Is Missing

The shop at m_inselburg_6529 has:
- Inventory sections: .items, .shopunits, .spells (all populated with expected data)
- Localization labels: itext_m_inselburg_6529_hint, itext_m_inselburg_6529_msg
- Shop marker: **`NPC_template@915`** (NOT `building_trader@`)
- Location: m_inselburg

The parser skips this shop because:
1. No standalone `itext_m_inselburg_6529` identifier exists (only `_hint` and `_msg` suffixes)
2. The shop uses `NPC_template@915` instead of `building_trader@`
3. The parser does not recognize `NPC_template@` as a valid shop marker

### Comparison with building_trader@ Shops

According to documentation, `building_trader@` shops have:
- `.actors` section with bit 7 set in strg field (active shop indicator)
- `building_trader@{num}` marker
- `lt` location tag

This NPC_template shop has:
- `.actors` section with bit 7 NOT set in strg field
- `NPC_template@{num}` marker instead
- `lt` location tag
- BUT: Still has populated inventory sections

### Parser Code Analysis

Line 292 in ShopInventoryParser.py:
```python
pos = data.find(b'building_trader@', pos)
```

This hardcoded search pattern excludes all `NPC_template@` shops, even if they have inventory.

## Conclusion

**Root Cause:** The ShopInventoryParser only recognizes two shop identifier patterns:
1. `itext_{location}_{number}` (without suffix)
2. `building_trader@{num}`

The missing shop uses a third pattern: **`NPC_template@{num}`** with localization labels that have `_hint` and `_msg` suffixes instead of a standalone shop ID.

**Impact:**
- All shops using `NPC_template@` markers are excluded from extraction
- Shops with only `itext_{id}_hint` / `itext_{id}_msg` labels (no standalone `itext_{id}`) are not detected

**Similar Cases:**
This is NOT an isolated case. Comprehensive analysis of the save file reveals:

**NPC_template@ Statistics:**
- Total NPC_template@ occurrences: 151
- NPC_template@ with inventory sections: 45 (29.8%)
- Section breakdown:
  - .items: 31 occurrences
  - .shopunits: 40 occurrences
  - .spells: 38 occurrences
  - .garrison: 0 occurrences

**Locations affected:**
- m_inselburg: 8 templates
- dragondor: 9 templates
- m_barazgund: 8 templates
- m_zcom: 8 templates
- m_bear_mountain: 7 templates
- m_portland: 7 templates
- And 14 other locations

**Comparison:**
- building_trader@ occurrences: 230
- NPC_template@ occurrences: 151
- Current parser extracts: 357 shops
- Estimated missing NPC_template shops: **~45 shops with inventory**

**Impact on Parser Coverage:**
The parser is missing approximately **11-12% of shops** (45 out of ~402 total shops).

**Recommendation:**
To extract this shop and similar ones, the parser would need to:
1. Add support for `NPC_template@` marker pattern
2. Handle localization labels with `_hint`/`_msg` suffixes as shop identifiers
3. Decide whether inactive shops (bit 7 not set) should be included if they have inventory
4. This would add approximately 45 shops to the extraction results

---

## Investigation Artifacts

All files created during this investigation are located in `/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/`:

**Data Files:**
- `decompressed_data.bin` (11 MB) - Decompressed save file for analysis
- `positions_context.txt` (8.2 KB) - Hex dump context around shop identifier positions

**Analysis Scripts:**
- `search_shop.py` - Search for shop identifier in decompressed data
- `examine_positions.py` - Examine context around shop identifier positions
- `search_inventory.py` - Search for expected inventory items by name and quantity
- `examine_shop_structure.py` - Analyze shop structure around inventory position
- `search_building_trader.py` - Search for building_trader@ patterns near m_inselburg
- `find_shop_marker.py` - Search backwards from inventory for shop markers
- `search_actors.py` - Examine .actors section for actor ID
- `search_forward.py` - Search forward from .temp for building_trader marker
- `count_npc_templates.py` - Count NPC_template@ occurrences in save file
- `check_npc_inventory.py` - Check how many NPC_template@ entries have inventory

**Commands Used:**
```bash
# Parse save file
docker exec kbtracker_app bash -c 's /app/tests/game_files/saves/quick1768586988'

# Run analysis scripts
docker exec kbtracker_app bash -c 'python /app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/search_shop.py'
docker exec kbtracker_app bash -c 'python /app/tests/research/save_decompiler/kb_shop_extractor/2026-01-16/count_npc_templates.py'
```
