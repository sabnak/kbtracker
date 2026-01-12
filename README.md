# King's Bounty Tracker

Веб-приложение для отслеживания предметов, заклинаний и существ в играх серии King's Bounty.

[English version below](#english-version)

---

## О приложении

King's Bounty Tracker помогает игрокам отслеживать местоположение предметов, заклинаний и существ в играх серии King's Bounty. Поскольку инвентарь торговцев генерируется случайно в каждой новой игре, этот инструмент позволяет записывать, где можно найти нужные предметы в вашем текущем прохождении.

## Ключевые возможности

### 📖 Просмотр игровой базы данных
- Просмотр всех предметов, заклинаний и существ из игры
- Подробная информация о каждой сущности (характеристики, описания, требования)
- Удобный поиск и фильтрация

### 🔍 Декомпилятор и парсер файлов сохранений
- Автоматическое извлечение данных из файлов сохранений
- Анализ инвентаря магазинов (предметы, заклинания, существа, гарнизоны)
- Поддержка всех объектов на карте с торговцами

### ✅ Отслеживание инвентаря (главная функция)
- **Полностью автоматическое отслеживание** инвентаря каждого магазина после простой настройки
- Отслеживание предметов, заклинаний, существ и гарнизонов
- Просмотр всех доступных товаров по магазинам и локациям
- История изменений инвентаря

### 👤 Множественные профили
- Создавайте отдельные профили для разных прохождений
- Каждый профиль имеет свою базу данных отслеживаемых объектов

### 🎮 Поддержка модифицированных игр
- Полная поддержка модифицированных версий игр
- Автоматическое определение новых предметов и сущностей из модов

### 🎯 Поддерживаемые игры

**На данный момент:**
- King's Bounty: Dark Side (включая мод Saturation)

**В перспективе:**
- King's Bounty: Warriors of the North
- King's Bounty: Crossworlds
- King's Bounty: Armored Princess
- King's Bounty: The Legend

## Установка

### Требования

Вам нужен только **Docker Desktop для Windows**: [Скачать Docker Desktop](https://www.docker.com/products/docker-desktop)

### Шаг 1: Скачайте docker-compose.yml

Скачайте файл: [docker-compose.yml](https://raw.githubusercontent.com/sabnak/kbtracker/main/docker-compose/user/docker-compose.yml)

Сохраните в папку на вашем компьютере (например, `C:/Games/KBTracker`)

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
- C:/Users/BORIS/Documents/my games/Kings Bounty The Dark Side/$$save/base/darkside:/saves/Darkside:ro
```

**Важно:**
- Используйте прямые слэши `/` (не обратные `\`)
- Сохраните `:ro` в конце (это делает папки доступными только для чтения)
- **Знак доллара `$` нужно удваивать:** если в пути есть `$save` пишите `$$save` в docker-compose.yml
- Путь к сохранениям должен вести к самим директориям, которые содержат сохранения игры.
  - Для Dark Side: `.../Documents/my gamesKings Bounty The Dark Side/$$save/base/darkside`
  - Для Crossworlds: `.../Documents/my games/Kings Bounty Crossworlds/$$save`
- Если в пути есть пробелы, возьмите весь путь в одинарные кавычки
- Можно добавлять несколько путей к играм и сохранениям. Формат всегда один:
```
- путь_на_вашем_компьютере:/data/название_игры:ro
```
  - "название_игры" при этом может быть любым, главное сохраните "/data/" в начале. Позднее вы сможете выбрать нужную игру в интерфейсе

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

## Управление приложением

### Остановка приложения

```bash
docker-compose down
```

### Обновление приложения

```bash
docker-compose pull
docker-compose up -d
```

### Удаление

Чтобы удалить всё включая базу данных:
```bash
docker-compose down -v
```

Это удалит все сохранённые данные о предметах и локациях!

## Технический стек

- **Backend**: FastAPI (Python 3.14)
- **Database**: PostgreSQL 16
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Architecture**: Domain-driven design with dependency injection
- **Deployment**: Docker Compose

## Поддержка

Сообщайте о проблемах: https://github.com/sabnak/kbtracker/issues

---

# English Version

Web application for tracking items, spells, and units in King's Bounty game series.

## About

King's Bounty Tracker helps players track the location of items, spells, and units in King's Bounty games. Since merchant inventories are randomly generated in each new game, this tool allows you to record where you can find the items you need in your current playthrough.

## Key Features

### 📖 In-Game Database Viewer
- View all items, spells, and units from the game
- Detailed information about each entity (stats, descriptions, requirements)
- Convenient search and filtering

### 🔍 Save File Decompiler and Parser
- Automatic data extraction from save files
- Shop inventory analysis (items, spells, units, garrisons)
- Support for all map objects with merchants

### ✅ Inventory Tracking (Main Feature)
- **Fully automated tracking** of every shop's inventory after simple configuration
- Track items, spells, units, and garrisons
- View all available goods by shops and locations
- Inventory change history

### 👤 Multiple Profiles
- Create separate profiles for different playthroughs
- Each profile has its own database of tracked objects

### 🎮 Modded Games Support
- Full support for modded game versions
- Automatic detection of new items and entities from mods

### 🎯 Supported Games

**Currently:**
- King's Bounty: Dark Side (including Saturation mod)

**Planned:**
- King's Bounty: Warriors of the North
- King's Bounty: Crossworlds
- King's Bounty: Armored Princess
- King's Bounty: The Legend

## Installation

### Prerequisites

You only need **Docker Desktop for Windows**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

### Step 1: Download docker-compose.yml

Download this file: [docker-compose.yml](https://raw.githubusercontent.com/sabnak/kbtracker/main/docker-compose/user/docker-compose.yml)

Save it to a folder on your computer (e.g., `C:/Games/KBTracker`)

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
- C:/Users/BORIS/Documents/my games/Kings Bounty The Dark Side/$$save/base/darkside:/saves/Darkside:ro
```

**Important:**
- Use forward slashes `/` (not backslashes `\`)
- Keep `:ro` at the end (makes volumes read-only)
- **Dollar sign `$` must be doubled:** if path contains `$save` write `$$save` in docker-compose.yml

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

## Application Management

### Stopping the Application

```bash
docker-compose down
```

### Updating the Application

```bash
docker-compose pull
docker-compose up -d
```

### Uninstalling

To remove everything including database:
```bash
docker-compose down -v
```

This removes all tracked items and game data!

## Tech Stack

- **Backend**: FastAPI (Python 3.14)
- **Database**: PostgreSQL 16
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Architecture**: Domain-driven design with dependency injection
- **Deployment**: Docker Compose

## Support

Report issues at: https://github.com/sabnak/kbtracker/issues
