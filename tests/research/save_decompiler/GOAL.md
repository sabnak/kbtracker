# Save Decompiler Research - Goals & Purpose

## Problem Statement

### Game Mechanics

In King's Bounty, when a player starts a new game:
- Every shop generates a **random assortment** of goods and units to hire
- Each save file contains this generated inventory data
- The game does not track which shops the player has visited

### User Challenge

Players need to track items available in shops to:
- Find specific items they need for their build
- Plan their shopping route efficiently
- Avoid missing unique items in shops they haven't visited
- Track stackable items (quantities are important)

**Current Problem:** Manually tracking shop inventories is tedious and error-prone, especially for shops with many items.

## Research Goals

### Primary Goal

**Extract shop inventory data from King's Bounty save files to automatically reveal shop assortments.**

### Specific Objectives

1. ✅ **Reverse-engineer save file format**
   - Understand the binary structure
   - Identify compression algorithm
   - Locate shop and item data

2. ✅ **Extract shop identifiers**
   - Find shop IDs in format: `itext_m_<location>_<number>`
   - Examples: `itext_m_galenirimm_2207`, `itext_m_helvedia_96`

3. ✅ **Extract item identifiers**
   - Find item IDs that can be matched with database
   - Examples: `itm_addon3_weapon_grandpa_sword`, `itm_addon2_gauntlet_avrelii_gauntlet`

4. ✅ **Create shop-to-items mapping**
   - Build complete data structure: `{shop_id: [item_ids]}`
   - Enable lookup of any shop's inventory

5. ✅ **Output in usable format**
   - JSON format for easy integration
   - Ready to import into application database

## User Story

**As a** King's Bounty player using the tracker app
**I want to** see what items are available in each shop
**So that** I can plan my purchases without manually checking each shop in-game

### Use Case

1. Player uploads their save file to the tracker
2. System parses save file and extracts shop inventories
3. Player views a location (e.g., "Galenirimm")
4. Player clicks **"Reveal Shop"** button
5. System displays all items available in that shop's generated assortment
6. Player can now:
   - See exactly what's available without visiting in-game
   - Track which items they've purchased
   - Plan their gold spending efficiently

## Why Manual Extraction Is Difficult

- **Large files:** Save files are 1.6MB compressed, 10.8MB decompressed
- **Binary format:** Custom game engine format, not documented
- **Mixed encodings:** UTF-16 for shop IDs, ASCII for item IDs
- **Complex structure:** Nested sections with variable-length data
- **No patterns visible:** Compressed data looks like random bytes

## What We Accomplished

### ✅ Successfully Solved

1. **Decompressed save files**
   - Identified "slcb" magic header
   - Detected zlib compression
   - Created decompressor

2. **Located shop data**
   - Found `.items` sections containing inventory
   - Identified shop ID storage (UTF-16 LE)
   - Identified item ID storage (ASCII, without "itm_" prefix)

3. **Extracted complete mappings**
   - **114 shops** with inventory data
   - **379 unique items** across all shops
   - JSON output ready for database import

4. **Created reusable parser**
   - `parse_shops_v2.py` can process any save file
   - Documented format for future maintenance
   - Clear integration path

### Example Output

```json
{
  "itext_m_galenirimm_2207": [
    "addon4_orc_primitive_sword",
    "addon2_gauntlet_avrelii_gauntlet",
    "addon4_spell_rock_blizzard_250"
  ],
  "itext_m_helvedia_96": [
    "addon3_weapon_grandpa_sword",
    "addon4_neutral_stone_helmet",
    "addon4_spell_rock_armageddon_250"
  ]
}
```

## Integration Goals

### Application Features to Build

1. **Save File Upload**
   - User uploads their save file
   - System validates and parses file
   - Extracts shop inventories

2. **Database Storage**
   ```sql
   CREATE TABLE save_shop_inventories (
       save_id VARCHAR,          -- Unique save identifier
       shop_id VARCHAR,          -- Shop text ID
       item_id VARCHAR,          -- Item ID (with itm_ prefix)
       PRIMARY KEY (save_id, shop_id, item_id)
   );
   ```

3. **UI Enhancement**
   - Add "Reveal Shop" button on location/shop pages
   - Display shop inventory from save data
   - Show item names, descriptions, icons from database
   - Allow users to mark items as "purchased"

4. **User Workflow**
   ```
   User → Upload Save → Parse → Store in DB → View Locations →
   Click "Reveal Shop" → See Items → Track Progress
   ```

## Important Notes

### Item ID Format

⚠️ **Critical:** Item IDs in save files **do NOT include** the "itm_" prefix!

- **Save file:** `addon4_orc_primitive_sword`
- **Database:** `itm_addon4_orc_primitive_sword`

**Solution:** Parser must prepend `itm_` when storing in database.

### Shop ID Format

Shop IDs match the format already in the database:
- `itext_m_<location>_<number>`
- Direct match with shop entries from KFS session files

### Data Completeness

- Not all shops may have items (some might be unit-only or spell-only)
- Parser extracted 114 shops from this specific save
- Different saves may have different numbers based on game progression

## Success Metrics

### Research Phase ✅ COMPLETE

- [x] Save file format documented
- [x] Decompression working
- [x] Shop IDs extracted
- [x] Item IDs extracted
- [x] Mappings created
- [x] JSON output generated
- [x] Parser tool created
- [x] Documentation written

### Integration Phase 🔄 NEXT STEPS

- [ ] Create SaveFileParser utility class
- [ ] Add database migration for shop inventories
- [ ] Implement file upload endpoint
- [ ] Build "Reveal Shop" UI component
- [ ] Add item purchase tracking
- [ ] Test with multiple save files

## Benefits to Users

### Time Savings
- **Before:** Visit each shop in-game, manually note items
- **After:** Upload save once, see all shops instantly

### Better Planning
- Know what's available before spending gold
- Find rare items across all shops
- Optimize travel routes

### Progress Tracking
- Mark items as purchased
- See what's left to buy
- Track expensive items for later

### Game Enhancement
- Doesn't modify game files (read-only)
- No cheating (items still must be purchased)
- Just provides information that's already in save file

## Conclusion

This research successfully reverse-engineered the King's Bounty save file format and created a working parser to extract shop inventory data. The hard work of understanding the binary format is complete.

**Next:** Integrate the parser into the main application to provide users with automatic shop inventory tracking - a feature that will significantly enhance their gameplay experience and save them hours of manual work.
