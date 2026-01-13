"""
Migration script to add sessions and saves_pattern columns to public.game table
"""
from src.core.Container import Container
from src.core.DefaultInstaller import DefaultInstaller


def main():
	"""
	Execute database migration to add sessions and saves_pattern columns
	"""
	container = Container()
	installer = DefaultInstaller(container)
	installer.install()

	schema_mgmt = container.schema_management_service()

	print("Starting migration: Adding sessions and saves_pattern to public.game table...")

	try:
		schema_mgmt.migrate_game_table_add_sessions_and_pattern()
		print("Migration completed successfully!")
	except Exception as e:
		print(f"Migration failed: {e}")
		raise


if __name__ == "__main__":
	main()
