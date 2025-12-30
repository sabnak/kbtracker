# King's Bounty Tracker 

## Project Overview

Application that allows users to track artifacts and scrolls in the King's Bounty.


## Schema-Based Multi-Tenancy

Each game has its own PostgreSQL schema (game_1, game_2, etc.). The `game` table lives in the `public` schema.

- **Game list** is retrieved from `public.game` table (shows all available games/schemas)
- **Game context** is determined by `game_id` in URL paths (`/games/{game_id}/...`)
- **Repository access** uses `GameContext` dependency injection and `_game_context` ContextVar
- **No game_id columns** in game-specific tables (items, locations, shops, profiles, etc.)
- **Session search_path** is set to the game's schema, automatically querying the correct data

Example: `/games/1/items` automatically queries `game_1.item` table.

## Project Tech Stack

@~/.ai_context/playbooks_create_instructions/inst-pps,pytest,di,fastapi,docker.md

@~/.ai_context/python.md
