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

## Development

### Running Tests

Tests will be added in a future version. Currently, manual testing is required.

### Adding New Features

The application follows domain-driven design principles:

1. **Domain Layer**: Add entities, interfaces, and services
2. **Infrastructure Layer**: Implement repository interfaces
3. **Web Layer**: Add routes and templates
4. **Dependency Injection**: Wire new components in AppInstaller

## Game Data Files

The application expects game data files in this format:

```
/data/
├── darkside/
│   ├── sessions/
│   │   ├── ses.kfs              # Game data
│   │   ├── loc_ses.kfs          # Russian localization
│   │   ├── loc_ses_eng.kfs      # English localization
│   │   ├── loc_ses_ger.kfs      # German localization
│   │   └── loc_ses_pol.kfs      # Polish localization
└── other_games/
    └── ...
```

KFS files are ZIP archives containing.