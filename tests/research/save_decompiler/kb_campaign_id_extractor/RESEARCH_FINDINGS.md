# Campaign ID Research - Findings Summary

## Research Objective
Find a unique, persistent campaign identifier in King's Bounty save files that:
- Remains identical across all saves within a campaign
- Differs between different campaigns
- Allows matching a new save to its campaign

## Test Data
- **Campaign 1:** Saves `1707078232`, `1707047253` (Feb 4, 2024)
- **Campaign 2:** Saves `1766864874`, `1767209722` (Dec 27 & 31, 2024)

## Investigations Performed

### 1. Info File Analysis
- **Result:** FAILED - No campaign ID found
- **Details:**
  - `session` field is identical for all saves (`base/darkside`)
  - File has variable-length fields, making offset comparison difficult
  - Only 4 discriminating bytes found, scattered throughout file
  - No consistent pattern

### 2. Decompressed Data File Analysis
- **Result:** FAILED - No campaign ID found
- **Details:**
  - First 1000 bytes are IDENTICAL across all 4 saves
  - Zero discriminating bytes in header region
  - All discriminating data appears 2MB+ into file (game state, not metadata)
  - "crap" field varies even within same campaign (random seed/session data)

### 3. Field Name Search
- **Result:** No ID fields found
- **Searched for:** `ugid`, `guid`, `uuid`, `cid`, `campaign_id`, `session_id`, `game_id`, `save_id`
- **Found:** None of these fields exist in the data

### 4. GUID/UUID Pattern Search
- **Result:** FAILED - No campaign ID found
- **Details:**
  - Searched for 128-bit values in first 50KB
  - Found 17,691 common offsets with high-entropy 16-byte values
  - **ZERO** candidates that match campaign ID criteria

### 5. Name File Analysis
- **Result:** NOT RELIABLE
- **Details:**
  - Campaign 2 saves share identical name ("Портланд" in Cyrillic)
  - Campaign 1 saves have different names
  - User-editable, not a reliable identifier

## Key Discoveries

### What We Know:
1. **All saves start identically** - First 1KB of decompressed data is the same
2. **No metadata-level campaign ID** - It's not in the header or early fields
3. **No standard ID field** - No `campaign_id`, `uuid`, `guid`, etc.
4. **Game state differs** - Discriminating data is deep in file (2MB+), representing game progression

### What We Don't Know:
1. **How does the game filter saves by campaign?**
2. **Is there a campaign ID at all, or does the game use another method?**
3. **Could the campaign ID be in a different file?** (not data/info/name/crc)
4. **Could it be a composite identifier?** (hash of multiple fields)

## Hypothesis: No Explicit Campaign ID Exists

### Alternative Theory
The game might NOT store an explicit campaign ID. Instead, it could:

1. **Use the first save's timestamp as campaign ID**
   - When starting a new campaign, first save's directory name (timestamp) becomes the "campaign ID"
   - All subsequent saves reference the original save somehow

2. **Use game state as implicit identifier**
   - The game might determine "same campaign" based on:
     - Character name
     - Current quest state
     - World map state
     - Some combination of game progression data

3. **Campaign filtering might be visual only**
   - User sees saves grouped by date/time proximity
   - Not actually filtering by campaign ID

## Questions for User

1. **How do you know the game filters saves by campaign?**
   - Do you see this in the game's load menu?
   - Or is it based on observation of save files?

2. **When you start a new campaign, what happens?**
   - Does the game create a "campaign file" somewhere?
   - Is there a campaign selection screen?

3. **Can you load a save from Campaign 1 while playing Campaign 2?**
   - Or does the game prevent this?
   - What error/behavior do you see?

4. **Are there any other files in the game's save directory?**
   - Maybe a `campaigns.dat` or `active_campaign.dat`?
   - Could you check: `Documents/my games/Kings Bounty The Dark Side/$save/base/`

## Next Steps

Depending on user answers:

1. **If there's a campaign file** → Analyze that file
2. **If saves reference first save** → Look for timestamp/filename references in data
3. **If it's game state based** → Compare character names, quest IDs, world state
4. **If no explicit ID exists** → Create composite identifier from multiple fields

## Tools Created

All research scripts in: `tests/research/save_decompiler/kb_campaign_id_extractor/`

- `find_campaign_id.py` - Binary comparison of info files
- `examine_header.py` - Info file header analysis
- `search_data_file.py` - Decompressed data search
- `deep_search.py` - Full file discriminating region search
- `search_ugid.py` - Field name search
- `dump_fields.py` - ASCII string extraction
- `extract_crap_field.py` - "crap" field analysis
- `check_name_files.py` - Name file decoder
- `find_guid_patterns.py` - GUID/UUID pattern search

## Conclusion

**No explicit campaign ID found in save files after extensive analysis.**

The campaign identifier might:
1. Not exist as a single field
2. Be derived from game state
3. Be stored externally (not in save files)
4. Use the first save's timestamp as reference

**USER INPUT NEEDED** to proceed with next research direction.
