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

## Quick Reference

| Resource Type | Archive Pattern | Database Table | Documentation |
|--------------|----------------|----------------|---------------|
| Localization | `loc_*.kfs` | `localization` | [localization.md](localization.md) |
| Items | `ses.kfs` | `item`, `item_set` | [items.md](items.md) |

## Key Concepts

**kb_id**: Unique in-game identifier used across all resources to reference game entities. Every resource (item, spell, unit, etc.) has a kb_id.

**KFS Archives**: ZIP-based archive files (`.kfs` extension) containing game resources. Can be extracted using standard ZIP tools or the project's KFSExtractor utility.

**Multi-tenancy**: Each game has its own PostgreSQL schema (`game_1`, `game_2`, etc.) containing extracted resource data.
