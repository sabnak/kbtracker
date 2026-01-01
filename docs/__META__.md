# Game Resources Documentation

## Overview

This documentation provides comprehensive guides for extracting and working with King's Bounty game resources. The documentation covers resource file formats, database structures, and extraction patterns.

**Target Audience**: AI agents and developers working with King's Bounty game data

## Available Documentation

### [game-resources.md](game-resources.md)
General overview of the game resources system. Covers:
- What are game resources
- Supported King's Bounty games and mods
- Resource location in filesystem
- KFS archive format
- Extraction tools
- Resource types (localization vs game data)
- kb_id concept

**Use this when**: You need to understand the overall structure of game resources or are just getting started.

### [localization.md](localization.md)
Detailed guide for localization resources extraction and usage. Covers:
- Database structure (`localization` table)
- Archive location patterns
- Language file formats
- Localization kb_id patterns
- SQL query examples
- BBCode/HTML tags in text

**Use this when**: You need to extract or work with game text translations, item names, descriptions, or any localized content.

### [items.md](items.md)
Detailed guide for item and item set resources. Covers:
- Database structures (`item` and `item_set` tables)
- Archive locations
- Item file format syntax
- Item properties (price, level, propbits)
- Item sets and relationships
- Localization integration

**Use this when**: You need to extract or work with game items, equipment, artifacts, or item collections.

### [save-extractor/](save-extractor/)
Save file extractor tool documentation. Contains complete guide for extracting shop inventory data from King's Bounty save files:
- **README.md**: Complete documentation with usage, technical details, troubleshooting
- **QUICKSTART.md**: 5-minute quick start guide
- **LIMITATIONS.md**: Magic constants explained with FAQ section
- **PRODUCTION_READY.md**: Production readiness checklist and validation results
- **example_usage.py**: Programmatic usage examples

**Tool location**: `/src/tools/kb_shop_extractor.py`

**Use this when**: You need to extract shop inventories (items, units, spells, garrison) from save files for analysis or integration.

### [campaign-identifier.md](campaign-identifier.md)
Campaign identification from save files. Covers:
- How to extract campaign ID from hero character names
- Programmatic usage and CLI interface
- Matching saves to campaigns
- Grouping saves by campaign
- Technical details and validation results

**Tool location**: `/src/tools/kb_campaign_identifier.py`

**Use this when**: You need to identify which campaign a save belongs to, or group saves by campaign since the game doesn't store explicit campaign IDs.

## Quick Reference

| Resource Type | Archive Pattern | Database Table | Documentation |
|--------------|----------------|----------------|---------------|
| Localization | `loc_*.kfs` | `localization` | [localization.md](localization.md) |
| Items | `ses.kfs` | `item`, `item_set` | [items.md](items.md) |
| Save Shops | Save file `data` | - | [save-extractor/](save-extractor/) |
| Campaign ID | Save file `data` | - | [campaign-identifier.md](campaign-identifier.md) |

## Key Concepts

**kb_id**: Unique in-game identifier used across all resources to reference game entities. Every resource (item, spell, unit, etc.) has a kb_id.

**KFS Archives**: ZIP-based archive files (`.kfs` extension) containing game resources. Can be extracted using standard ZIP tools or the project's KFSExtractor utility.

**Multi-tenancy**: Each game has its own PostgreSQL schema (`game_1`, `game_2`, etc.) containing extracted resource data.
