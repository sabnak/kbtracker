-- Migration: Rename game_version to game_path in profile table
-- Date: 2025-12-28
-- Description: Rename the game_version column to game_path to better reflect that it stores the relative path to game data

-- Check if the game_version column exists before attempting to rename it
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'profile'
        AND column_name = 'game_version'
    ) THEN
        -- Rename the column from game_version to game_path
        ALTER TABLE profile RENAME COLUMN game_version TO game_path;
        RAISE NOTICE 'Column game_version renamed to game_path';
    ELSE
        RAISE NOTICE 'Column game_version does not exist, skipping rename';
    END IF;

    -- Also add created_at column if it doesn't exist (for older schemas)
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'profile'
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE profile ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Column created_at added to profile table';
    END IF;
END $$;
