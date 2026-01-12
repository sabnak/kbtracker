# Translation Workflow

## Overview

This project uses Babel (pybabel) for internationalization (i18n) with support for Russian and English languages.

## File Structure

```
src/i18n/
├── messages.pot                           # Template file (NOT in git)
└── translations/
    ├── en/LC_MESSAGES/
    │   ├── messages.po                    # English translations (IN GIT)
    │   └── messages.mo                    # Compiled binary (NOT in git)
    └── ru/LC_MESSAGES/
        ├── messages.po                    # Russian translations (IN GIT)
        └── messages.mo                    # Compiled binary (NOT in git)
```

## Workflow Commands

### 1. Extract Messages from Code

Extract all translatable strings from Python code and Jinja2 templates:

```bash
docker exec kbtracker_app bash -c 'cd /app && pybabel extract -F babel.cfg -k _ --no-location -o src/i18n/messages.pot .'
```

**Note:** The `--no-location` flag prevents adding location comments to the .pot file.

### 2. Update Translation Catalogs

Update .po files with new/changed strings from the .pot template:

```bash
docker exec kbtracker_app bash -c 'cd /app && pybabel update -i src/i18n/messages.pot -d src/i18n/translations'
```

**Note:** This command merges new strings from .pot into existing .po files while preserving existing translations.

### 3. Compile Translations (Manual)

Compile .po files to .mo binary files for use at runtime:

```bash
docker exec kbtracker_app bash -c 'cd /app && pybabel compile -d src/i18n/translations'
```

**Note:** This is done automatically on container startup via entrypoint script.

## Typical Workflow

### Adding New Translatable String to Template

1. Add translation key to your template:
   ```html
   <h1>{{ _('ui.my_new_key') }}</h1>
   ```

2. Extract messages to update .pot file:
   ```bash
   docker exec kbtracker_app bash -c 'cd /app && pybabel extract -F babel.cfg -k _ --no-location -o src/i18n/messages.pot .'
   ```

3. Update .po files:
   ```bash
   docker exec kbtracker_app bash -c 'cd /app && pybabel update -i src/i18n/messages.pot -d src/i18n/translations'
   ```

4. Edit `src/i18n/translations/en/LC_MESSAGES/messages.po` and add English translation:
   ```po
   msgid "ui.my_new_key"
   msgstr "My New Translation"
   ```

5. Edit `src/i18n/translations/ru/LC_MESSAGES/messages.po` and add Russian translation:
   ```po
   msgid "ui.my_new_key"
   msgstr "Мой новый перевод"
   ```

6. Commit changes to git:
   ```bash
   git add src/i18n/translations/*/LC_MESSAGES/messages.po
   git commit -m "Add translation for ui.my_new_key"
   ```

**Note:** You don't need to manually compile - the Docker container will compile translations automatically on startup.

## Git Rules

**Commit to git:**
- ✅ `.po` files (source translations)
- ✅ `.gitignore` (to exclude generated files)

**Do NOT commit:**
- ❌ `.mo` files (compiled binaries)
- ❌ `.pot` files (can be regenerated)

## Automatic Compilation

The Docker entrypoint script (`docker-compose/app/entrypoint.sh`) automatically compiles translations on container startup:

```bash
#!/bin/bash
set -e

echo "==================================="
echo "Compiling translations..."
echo "==================================="
cd /app && pybabel compile -d src/i18n/translations

echo "==================================="
echo "Starting supervisord..."
echo "==================================="
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
```

This means:
- Developers don't need to manually compile translations
- Every container start ensures fresh .mo files
- Uvicorn's `--reload` flag still works for code changes
- No need to restart container when editing templates

## Translation Key Conventions

Use symbolic keys with prefixes:

- **`ui.*`** - UI-related strings (buttons, labels, navigation)
  - Example: `ui.games`, `ui.create_new_game`, `ui.delete`

- **`game.*`** - Game-related data (future use)
  - Example: `game.spell_name`, `game.item_description`

## Language Configuration

Current language is determined by `settings_service.get_settings().language`:

- `AppLanguage.RUSSIAN` → locale `ru`
- `AppLanguage.ENGLISH` → locale `en`

Users can change language in the Settings page (`/settings`).
