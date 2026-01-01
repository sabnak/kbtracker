# King's Bounty Tracker 

## Project Overview

Application that allows users to track artifacts and scrolls in the King's Bounty.

## Game Resources Documentation

The `/docs` folder contains comprehensive guides for extracting and working with King's Bounty game resources.

- **Documentation Index**: `__META__.md` is the main index listing all available documentation
- **Contents**: Resource file formats (KFS archives), database structures, extraction patterns, localization guides, item data formats
- **Target Audience**: AI agents and developers working with King's Bounty game data
- **Key Topics**: game resources overview, localization extraction, item/item set resources, kb_id concept
- **Access**: Always check `__META__.md` first to find the relevant documentation file for your task

## Schema-Based Multi-Tenancy

Each game has its own PostgreSQL schema (game_1, game_2, etc.). The `game` table lives in the `public` schema.

- **Game list** is retrieved from `public.game` table (shows all available games/schemas)
- **Game context** is determined by `game_id` in URL paths (`/games/{game_id}/...`)
- **Repository access** uses `GameContext` dependency injection and `_game_context` ContextVar
- **No game_id columns** in game-specific tables (items, locations, shops, profiles, etc.)
- **Session search_path** is set to the game's schema, automatically querying the correct data

Example: `/games/1/items` automatically queries `game_1.item` table.

## Docker Environment

**MANDATORY**: Application runs in Docker container.

- **Container name**: `kbtracker_app`
- **All application scripts MUST run inside the container**
- **Tests MUST be run in the container**: `docker exec kbtracker_app bash -c 'cd /app && pytest'`
- **Never run application code on host machine**

## Database Operations

**MANDATORY**: For executing raw SQL queries, you MUST use the toolbox MCP server.

- **Tool**: `mcp__toolbox__execute_postgresq_local-tool`
- **Do NOT use**: `docker exec` with psql or other direct database commands
- **Always use the MCP tool** for any SQL operations

## Project Tech Stack

@~/.ai_context/python.md