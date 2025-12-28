# Database Migrations

This directory contains database migration scripts for the King's Bounty Tracker project.

## Running Migrations

To apply a migration to your existing database, execute the following command:

```bash
docker exec kbtracker_postgres psql -U <DB_USER> -d <DB_NAME> -f /migrations/<migration_file>.sql
```

Replace `<DB_USER>` and `<DB_NAME>` with your actual database credentials from your `.env` file.

### Example

To apply the game_version to game_path migration:

```bash
docker exec kbtracker_postgres psql -U kbtracker -d kbtracker -f /migrations/001_rename_game_version_to_game_path.sql
```

**Note:** You'll need to mount the migrations directory in your docker-compose.yml for this to work:

```yaml
postgres:
  volumes:
    - ./migrations:/migrations
```

## Alternative Method: Direct SQL Execution

You can also copy the SQL content and execute it directly:

```bash
docker exec -i kbtracker_postgres psql -U <DB_USER> -d <DB_NAME> < migrations/001_rename_game_version_to_game_path.sql
```

## Migration List

- `001_rename_game_version_to_game_path.sql` - Renames the `game_version` column to `game_path` in the profile table
