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

## Database-per-Game Multi-Tenancy (SQLite)

The application uses SQLite. Each game has its own database file; a shared
application database holds cross-game tables.

- **Storage layout**: `DATABASE_DIR` holds `app.db` (shared) plus one
  `game_<id>.db` file per game. `DATABASE_DIR` defaults to `<project_root>/db`.
- **Shared `app.db`** holds the `game` and `meta` tables.
- **Game list** is retrieved from the `game` table in `app.db`.
- **Game context** is determined by `game_id` in URL paths (`/games/{game_id}/...`).
- **Repository access** uses `GameContext` dependency injection and the
  `GAME_CONTEXT` ContextVar. When a game context is set, `CrudRepository`
  resolves the matching `game_<id>.db` session via the `GameDatabaseRegistry`
  (`src/utils/db.py`); otherwise it uses the shared `app.db` session.
- **No game_id columns** in game-specific tables (items, locations, shops,
  profiles, etc.) — each game's data lives in its own file. The `profile`
  table keeps a plain `game_id` value (no cross-database foreign key).
- **Schema creation** is driven by the SQLAlchemy mappers via
  `Base.metadata.create_all`, not hand-written DDL (`SchemaManagementService`).

Example: `/games/1/items` queries the `item` table inside `game_1.db`.

## Database Operations

For executing raw SQL queries against the SQLite databases, connect directly
to the relevant file under `DATABASE_DIR` (`app.db` or `game_<id>.db`) using
SQLAlchemy or the `sqlite3` CLI. There is no separate database server.

## Running and Testing

The application no longer requires a database server, so it can run and be
tested either inside the Docker container (`kbtracker_app`) or natively.

- **Docker**: `docker exec kbtracker_app bash -c 'cd /app && pytest'`
- **Native**: run `pytest` against the project venv with `DATABASE_DIR` set to
  a writable directory.

## Project Tech Stack

@~/.ai_context/python.md