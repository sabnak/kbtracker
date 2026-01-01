# Campaign Identifier Extraction

## Overview

King's Bounty: The Dark Side does not store an explicit campaign ID in save files. To identify which saves belong to the same campaign, we use the **hero's character names** (first and second name) as a composite identifier.

This creates a unique campaign ID by hashing the hero's full name, allowing you to match new saves to existing campaigns.

## Quick Start

```python
from pathlib import Path
from tools.kb_campaign_identifier import extract_campaign_id

# Extract campaign ID from a save file
save_path = Path('path/to/save/directory/data')
result = extract_campaign_id(save_path)

print(f"Campaign ID: {result['campaign_id']}")
print(f"Hero name: {result['full_name']}")
# Output:
# Campaign ID: 67c69e2f669989e937aa367ba355b57e
# Hero name: Неолина Очаровательная
```

## How It Works

### Campaign Identification Strategy

1. **Decompress save file** - Extract data from compressed `data` file
2. **Scan for character names** - Find UTF-16LE encoded Cyrillic strings
3. **Extract hero names** - Skip pet name, take first and second hero names
4. **Generate campaign ID** - Create MD5 hash: `MD5(first_name|second_name)`

### Why This Works

- Hero names are set when starting a new campaign
- Names remain constant throughout the campaign
- Different campaigns have different character names
- MD5 hash provides consistent, short identifier

### Limitations

**Not Guaranteed Unique**: Two campaigns with identical hero names will have the same ID. However, this is acceptable because:
- Players rarely use identical character names
- The collision probability is very low in practice
- If collision occurs, campaigns are essentially indistinguishable anyway

## Command Line Usage

```bash
# Basic usage
python src/tools/kb_campaign_identifier.py path/to/save/data

# Example with actual path
python src/tools/kb_campaign_identifier.py "c:/Users/UserName/Documents/my games/Kings Bounty The Dark Side/$save/base/darkside/1707078232/data"
```

**Output:**
```
============================================================
CAMPAIGN IDENTIFIER EXTRACTION
============================================================

Save file: path/to/save/data

Hero name: Неолина Очаровательная
  First name:  Неолина
  Second name: Очаровательная

Campaign ID: 67c69e2f669989e937aa367ba355b57e
```

## Programmatic Usage

### Basic Extraction

```python
from pathlib import Path
from tools.kb_campaign_identifier import extract_campaign_id

save_data_file = Path('/path/to/save/data')
result = extract_campaign_id(save_data_file)

# Result structure:
# {
#     'campaign_id': '67c69e2f669989e937aa367ba355b57e',
#     'first_name': 'Неолина',
#     'second_name': 'Очаровательная',
#     'full_name': 'Неолина Очаровательная'
# }
```

### Matching Saves to Campaigns

```python
from pathlib import Path
from tools.kb_campaign_identifier import extract_campaign_id

def match_save_to_campaign(
	new_save_path: Path,
	known_campaigns: dict[str, list[Path]]
) -> str | None:
	"""
	Match a new save to known campaigns.

	:param new_save_path:
		Path to new save's data file
	:param known_campaigns:
		Dictionary mapping campaign_id to list of save paths
	:return:
		Campaign ID if matched, None if new campaign
	"""
	result = extract_campaign_id(new_save_path)
	campaign_id = result['campaign_id']

	if campaign_id in known_campaigns:
		return campaign_id

	return None  # New campaign


# Usage example
known_campaigns = {
	'67c69e2f669989e937aa367ba355b57e': [
		Path('/saves/1707078232/data'),
		Path('/saves/1707047253/data')
	],
	'3b1fd3c524a9fd4890ec37f14bae8bc0': [
		Path('/saves/1766864874/data')
	]
}

new_save = Path('/saves/1767209722/data')
campaign_id = match_save_to_campaign(new_save, known_campaigns)

if campaign_id:
	print(f"Save belongs to existing campaign: {campaign_id}")
else:
	print("This is a new campaign!")
```

### Group Saves by Campaign

```python
from pathlib import Path
from tools.kb_campaign_identifier import extract_campaign_id
from collections import defaultdict

def group_saves_by_campaign(save_paths: list[Path]) -> dict[str, list[Path]]:
	"""
	Group save files by campaign.

	:param save_paths:
		List of paths to save data files
	:return:
		Dictionary mapping campaign_id to list of save paths
	"""
	campaigns = defaultdict(list)

	for save_path in save_paths:
		try:
			result = extract_campaign_id(save_path)
			campaign_id = result['campaign_id']
			campaigns[campaign_id].append(save_path)
		except Exception as e:
			print(f"Error processing {save_path}: {e}")

	return dict(campaigns)


# Usage
save_dir = Path('c:/Users/UserName/Documents/my games/Kings Bounty The Dark Side/$save/base/darkside')
all_saves = [d / 'data' for d in save_dir.iterdir() if d.is_dir() and (d / 'data').exists()]

campaigns = group_saves_by_campaign(all_saves)

for campaign_id, saves in campaigns.items():
	print(f"\nCampaign {campaign_id}:")
	print(f"  {len(saves)} saves")
	for save in saves:
		print(f"    - {save.parent.name}")
```

## Technical Details

### Save File Format

The `data` file uses the following format:
- **4 bytes**: Magic header `slcb`
- **4 bytes**: Decompressed size (uint32 little-endian)
- **4 bytes**: Compressed size (uint32 little-endian)
- **N bytes**: zlib compressed game state data

### Character Name Extraction

Names are stored as **UTF-16LE** encoded strings in the decompressed data:
- **Pet name**: First Cyrillic string found (ignored)
- **Hero first name**: Second Cyrillic string found
- **Hero second name**: Third Cyrillic string found

The extractor scans the first 100KB of decompressed data and filters out game keywords to identify actual character names.

### Campaign ID Generation

```python
campaign_id = MD5(f"{first_name}|{second_name}")
```

Example:
```
Hero: "Неолина Очаровательная"
→ MD5("Неолина|Очаровательная")
→ "67c69e2f669989e937aa367ba355b57e"
```

## Error Handling

The tool raises exceptions for:
- **Invalid file format**: Missing or incorrect magic header
- **Decompression errors**: Corrupted zlib data
- **Size mismatch**: Decompressed size doesn't match header

```python
from tools.kb_campaign_identifier import extract_campaign_id

try:
	result = extract_campaign_id(save_path)
except ValueError as e:
	print(f"Invalid save file: {e}")
except Exception as e:
	print(f"Error extracting campaign ID: {e}")
```

## Validation Results

**Test Data**:
- Campaign 1: Hero "Неолина Очаровательная" (2 saves)
- Campaign 2: Hero "Даэрт де Мортон" (2 saves)

**Results**:
- ✅ Campaign 1 saves share same ID: `67c69e2f669989e937aa367ba355b57e`
- ✅ Campaign 2 saves share same ID: `3b1fd3c524a9fd4890ec37f14bae8bc0`
- ✅ Campaign IDs differ between campaigns
- ✅ **100% accuracy**

## FAQ

### Q: Can I use this for other King's Bounty games?

The tool is designed for **King's Bounty: The Dark Side**. Other King's Bounty games may use different save formats and would require verification/modification.

### Q: What if two campaigns have the same hero name?

They will have identical campaign IDs. This is rare in practice since players typically use unique character names. If this is a concern for your use case, you could add additional data to the hash (e.g., campaign creation timestamp from save directory name).

### Q: Does this work with modded games?

Yes, as long as the save file format remains the same. The tool only reads character names, which are standard across mods.

### Q: What if character names are changed mid-campaign?

If the game allows renaming the hero (uncommon), the campaign ID will change. The tool assumes character names are immutable after campaign creation.

## See Also

- [Game Resources Overview](game-resources.md) - General game resource information
- [Save Shop Extractor](save-extractor/) - Extract shop inventories from saves
