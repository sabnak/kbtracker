# King's Bounty Tracker - Инструкция по установке для игроков

[English version below](#english-version)

## Требования

Вам нужен только **Docker Desktop для Windows**: [Скачать Docker Desktop](https://www.docker.com/products/docker-desktop)

## Установка

### Шаг 1: Скачайте docker-compose.yml

Скачайте файл: [docker-compose.yml](https://raw.githubusercontent.com/sabnak/kbtracker/main/docker-compose.user.yml)

Сохраните в папку на вашем компьютере (например, `C:\KBTracker\`)

### Шаг 2: Укажите пути к игре

Откройте `docker-compose.yml` в текстовом редакторе (Блокнот, VS Code и т.д.)

Найдите эти строки:
```yaml
- /path/to/your/game/Darkside:/data/Darkside:ro
- /path/to/your/saves/Darkside:/saves/Darkside:ro
```

**Замените на ваши реальные пути:**

#### Пример:
```yaml
- C:/Program Files (x86)/Steam/steamapps/common/Darkside:/data/Darkside:ro
- C:/Users/BORIS/Documents/my games/Kings Bounty The Dark Side/$$$$save/base/darkside:/saves/Darkside:ro
```

**Важно:**
- Используйте прямые слэши `/` (не обратные `\`)
- Сохраните `:ro` в конце (это делает папки доступными только для чтения)
- **Знак доллара `$` нужно удваивать:** если в пути есть `$save`, пишите `$$save` → `$$$$save` в docker-compose.yml
- Если в пути есть пробелы и возникают проблемы, возьмите весь путь в одинарные кавычки

### Шаг 3: Запустите приложение

Откройте командную строку (cmd) или PowerShell в папке с `docker-compose.yml`:

```bash
docker-compose up -d
```

Это:
- Скачает готовое приложение (~200MB)
- Скачает PostgreSQL базу данных (~100MB)
- Запустит оба контейнера

### Шаг 4: Откройте приложение

Откройте браузер и перейдите:
```
http://localhost:9333
```

## Как найти пути к игре

### Папка установки игры (Steam)

В Steam:
- ПКМ на игре → Управление → Просмотреть локальные файлы
- Обычный путь: `C:/Program Files (x86)/Steam/steamapps/common/Darkside`

### Папка сохранений

Сохранения всех игр серии King's Bounty находятся в:
```
C:/Users/[ВашеИмя]/Documents/my games/
```

Пример для Dark Side:
```
C:/Users/BORIS/Documents/my games/Kings Bounty The Dark Side/$$save/base/darkside
```

**Не забудьте удвоить `$$` при указании пути в docker-compose.yml!**

## Остановка приложения

```bash
docker-compose down
```

## Обновление приложения

```bash
docker-compose pull
docker-compose up -d
```

## Удаление

Чтобы удалить всё включая базу данных:
```bash
docker-compose down -v
```

Это удалит все сохранённые данные о предметах и локациях!

## Поддержка

Сообщайте о проблемах: https://github.com/sabnak/kbtracker/issues

---

# English Version

## Prerequisites

You only need **Docker Desktop for Windows**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

## Installation Steps

### Step 1: Download docker-compose.yml

Download this file: [docker-compose.yml](https://raw.githubusercontent.com/sabnak/kbtracker/main/docker-compose.user.yml)

Save it to a folder on your computer (e.g., `C:\KBTracker\`)

### Step 2: Edit Volume Paths

Open `docker-compose.yml` in a text editor (Notepad, VS Code, etc.)

Find these lines:
```yaml
- /path/to/your/game/Darkside:/data/Darkside:ro
- /path/to/your/saves/Darkside:/saves/Darkside:ro
```

**Replace with your actual paths:**

#### Example:
```yaml
- C:/Program Files (x86)/Steam/steamapps/common/Darkside:/data/Darkside:ro
- C:/Users/BORIS/Documents/my games/Kings Bounty The Dark Side/$$$$save/base/darkside:/saves/Darkside:ro
```

**Important:**
- Use forward slashes `/` (not backslashes `\`)
- Keep `:ro` at the end (makes volumes read-only)
- **Dollar sign `$` must be doubled:** if path contains `$save`, write `$$save` → `$$$$save` in docker-compose.yml
- Quote entire path with single quotes if spaces cause issues

### Step 3: Start the Application

Open Command Prompt (cmd) or PowerShell in the folder with `docker-compose.yml`:

```bash
docker-compose up -d
```

This will:
- Download the pre-built application (~200MB)
- Download PostgreSQL database (~100MB)
- Start both containers

### Step 4: Access the Application

Open your browser and go to:
```
http://localhost:9333
```

## Finding Your Game Paths

### Game Installation Directory (Steam)

In Steam:
- Right-click game → Manage → Browse local files
- Common path: `C:/Program Files (x86)/Steam/steamapps/common/Darkside`

### Save Files Directory

Save files for all King's Bounty games are located in:
```
C:/Users/[YourName]/Documents/my games/
```

Example for Dark Side:
```
C:/Users/BORIS/Documents/my games/Kings Bounty The Dark Side/$$save/base/darkside
```

**Don't forget to double `$$` when specifying the path in docker-compose.yml!**

## Stopping the Application

```bash
docker-compose down
```

## Updating the Application

```bash
docker-compose pull
docker-compose up -d
```

## Uninstalling

To remove everything including database:
```bash
docker-compose down -v
```

This removes all tracked items and game data!

## Support

Report issues at: https://github.com/sabnak/kbtracker/issues
