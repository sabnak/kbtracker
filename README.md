# King's Bounty Tracker

A web application for tracking items, merchants, and locations in the King's Bounty game series.

## Overview

King's Bounty Tracker helps players keep track of item locations across multiple game playthroughs. Since merchant inventories are randomly generated with each new game, this tool allows you to record where specific items can be found.

## Supported Games

- King's Bounty: Dark Side
- King's Bounty: Warriors of the North
- King's Bounty: Crossworlds
- King's Bounty: Armored Princess
- King's Bounty: The Legend

## Features

- **Profile Management**: Create multiple game profiles to track different playthroughs
- **Game File Scanning**: Scan game data files to populate item and merchant databases
- **Item Tracking**: Record which items are available in which merchant shops
- **Search Functionality**: Search through items to find what you need
- **Location Organization**: Items organized by location and merchant

## Tech Stack

- **Backend**: FastAPI (Python 3.14)
- **Database**: PostgreSQL 16
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Architecture**: Domain-driven design with dependency injection
- **Deployment**: Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- King's Bounty game files accessible on your system

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kbtracker
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Edit `.env` if needed (default values should work for most cases)

4. Edit `docker-compose.yml` to mount your game directories:
```yaml
services:
  app:
    volumes:
      - .:/app
      # Add your game directories here (read-only):
      - /path/to/your/game/darkside:/data/darkside:ro
```

5. Start the application:
```bash
docker-compose up -d
```

6. Access the application at: http://localhost:9333

### Stopping the Application

```bash
docker-compose down
```

To remove all data (including database):
```bash
docker-compose down -v
```

## Usage

### Creating a Profile

1. Navigate to http://localhost:9333
2. Click "Create New Profile"
3. Enter a profile name and select your game version
4. Click "Create Profile"

### Scanning Game Files

1. From the profile list, click "Scan" on your profile
2. Select the language version of your game
3. Click "Start Scan"

**Note**: The scanner functionality is currently a stub and will show an error. The actual game file parsing will be implemented in a future version.

### Tracking Items

1. Click "Items" on your profile
2. Search for an item or browse the list
3. Click "Track" on an item
4. Select the location and merchant where you found it
5. Enter the quantity available
6. Click "Save"

### Viewing Tracked Items

1. Click "Tracked" on your profile
2. View all items you've recorded with their locations

## Project Structure

```
kbtracker/
├── docker-compose/          # Docker configuration
│   └── app/
│       └── Dockerfile
├── src/
│   ├── domain/              # Domain layer (entities, interfaces, services)
│   ├── infrastructure/      # Infrastructure layer (repositories, database)
│   ├── web/                 # Web layer (routes, templates, static files)
│   ├── di/                  # Dependency injection configuration
│   ├── config.py            # Application configuration
│   └── main.py              # Application entry point
├── docker-compose.yml       # Docker services definition
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Development

### Running Tests

Tests will be added in a future version. Currently, manual testing is required.

### Adding New Features

The application follows domain-driven design principles:

1. **Domain Layer**: Add entities, interfaces, and services
2. **Infrastructure Layer**: Implement repository interfaces
3. **Web Layer**: Add routes and templates
4. **Dependency Injection**: Wire new components in AppInstaller

## Roadmap

- [ ] Implement game file scanner (KFS archive parsing)
- [ ] Add automated save file analysis
- [ ] Implement item filtering by type
- [ ] Add export functionality
- [ ] Create API endpoints for external tools
- [ ] Add unit and integration tests
- [ ] Implement database migrations with Alembic

## Game Data Files

The application expects game data files in this format:

```
/data/
├── darkside/
│   ├── loc_ses.kfs          # Russian version
│   ├── loc_ses_eng.kfs      # English version
│   ├── loc_ses_ger.kfs      # German version
│   └── loc_ses_pol.kfs      # Polish version
└── other_games/
    └── ...
```

KFS files are ZIP archives containing:
- `rus_items.lng` - Item definitions
- `rus_atoms_info.lng` - Merchant/object definitions

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Check that PostgreSQL container is running: `docker-compose ps`
2. Wait a few seconds for the health check to pass
3. Restart the app container: `docker-compose restart app`

### Port Already in Use

If port 9333 is already in use:
1. Edit `.env` and change `APP_PORT` to a different port
2. Restart: `docker-compose down && docker-compose up -d`

### Game Files Not Found

Ensure your game directories are correctly mounted in `docker-compose.yml`:
- Paths must be absolute
- Use `:ro` (read-only) flag for safety
- The directory structure inside the container should match the game version name

## License

This project is for personal use. King's Bounty is a trademark of its respective owners.

## Contributing

This is a personal project, but suggestions and feedback are welcome!
