-- King's Bounty Tracker Database Schema

-- Create game table first (referenced by all other tables)
CREATE TABLE game (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	path VARCHAR(100) NOT NULL UNIQUE
);

-- Create index for path lookups
CREATE INDEX idx_game_path ON game(path);

-- Create profile table (referenced by shops_has_items)
CREATE TABLE profile (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	game_id INTEGER NOT NULL,
	created_at TIMESTAMP NOT NULL,
	CONSTRAINT fk_profile_game FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE
);

-- Create index for game_id in profile
CREATE INDEX idx_profile_game_id ON profile(game_id);

-- Create location table (referenced by shop)
CREATE TABLE location (
	id SERIAL PRIMARY KEY,
	game_id INTEGER NOT NULL,
	kb_id VARCHAR(255) NOT NULL,
	name VARCHAR(255) NOT NULL,
	CONSTRAINT fk_location_game FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE,
	UNIQUE(game_id, kb_id)
);

-- Create indexes for game_id and kb_id in location
CREATE INDEX idx_location_game_id ON location(game_id);
CREATE INDEX idx_location_kb_id ON location(kb_id);

-- Create item table (referenced by shops_has_items)
CREATE TABLE item (
	id SERIAL PRIMARY KEY,
	game_id INTEGER NOT NULL,
	kb_id VARCHAR(255) NOT NULL,
	name VARCHAR(255) NOT NULL,
	price INTEGER NOT NULL,
	hint TEXT,
	propbits VARCHAR(255)[],
	CONSTRAINT fk_item_game FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE,
	UNIQUE(game_id, kb_id)
);

-- Create indexes for game_id and kb_id in item
CREATE INDEX idx_item_game_id ON item(game_id);
CREATE INDEX idx_item_kb_id ON item(kb_id);

-- Create shop table (referenced by shops_has_items)
CREATE TABLE shop (
	id SERIAL PRIMARY KEY,
	game_id INTEGER NOT NULL,
	kb_id VARCHAR(255) NOT NULL,
	location_id INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL,
	hint TEXT,
	msg TEXT,
	CONSTRAINT fk_shop_game FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE,
	CONSTRAINT fk_shop_location FOREIGN KEY (location_id) REFERENCES location(id) ON DELETE CASCADE,
	UNIQUE(game_id, kb_id)
);

-- Create indexes for shop
CREATE INDEX idx_shop_game_id ON shop(game_id);
CREATE INDEX idx_shop_location_id ON shop(location_id);
CREATE INDEX idx_shop_kb_id ON shop(kb_id);

-- Create junction table for shops and items
CREATE TABLE shops_has_items (
	item_id INTEGER NOT NULL,
	shop_id INTEGER NOT NULL,
	profile_id INTEGER NOT NULL,
	count INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY (item_id, shop_id, profile_id),
	CONSTRAINT fk_shops_has_items_item FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE,
	CONSTRAINT fk_shops_has_items_shop FOREIGN KEY (shop_id) REFERENCES shop(id) ON DELETE CASCADE,
	CONSTRAINT fk_shops_has_items_profile FOREIGN KEY (profile_id) REFERENCES profile(id) ON DELETE CASCADE
);

-- Create indexes for foreign keys in junction table
CREATE INDEX idx_shops_has_items_item_id ON shops_has_items(item_id);
CREATE INDEX idx_shops_has_items_shop_id ON shops_has_items(shop_id);
CREATE INDEX idx_shops_has_items_profile_id ON shops_has_items(profile_id);
