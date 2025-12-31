-- Migration: Add tiers column to item table
-- Description: Adds tiers VARCHAR(255)[] column to store upgrade tier chain kb_ids
-- Date: 2025-12-31

DO $$
DECLARE
	schema_name text;
BEGIN
	FOR schema_name IN
		SELECT nspname
		FROM pg_namespace
		WHERE nspname LIKE 'game_%'
	LOOP
		EXECUTE format('ALTER TABLE %I.item ADD COLUMN IF NOT EXISTS tiers VARCHAR(255)[]', schema_name);
	END LOOP;
END $$;
