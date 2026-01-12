# User Docker Compose Configuration

Эта директория содержит готовую конфигурацию для конечных пользователей.

This directory contains ready-to-use configuration for end users.

---

## Русский

### Использование

1. Скопируйте файл `docker-compose.yml` на ваш компьютер
2. Отредактируйте пути к игре в секции `volumes`
3. В папке с файлом выполните:
   ```bash
   docker-compose up -d
   ```

### Что находится внутри

- Использует готовый образ из GitHub Container Registry (`ghcr.io/sabnak/kbtracker:latest`)
- Настроенный PostgreSQL
- Готовые переменные окружения

### Подробная инструкция

См. [INSTALL.md](../../INSTALL.md) в корне репозитория

---

## English

### Usage

1. Copy `docker-compose.yml` file to your computer
2. Edit game paths in the `volumes` section
3. In the folder with the file, run:
   ```bash
   docker-compose up -d
   ```

### What's Inside

- Uses pre-built image from GitHub Container Registry (`ghcr.io/sabnak/kbtracker:latest`)
- Configured PostgreSQL
- Ready-to-use environment variables

### Detailed Instructions

See [INSTALL.md](../../INSTALL.md) in the repository root
