-- King's Bounty Tracker Database Schema

-- Create profile table first (referenced by objects_has_items)
CREATE TABLE profile (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL
);

-- Create location table (referenced by object)
CREATE TABLE location (
	id SERIAL PRIMARY KEY,
	kb_id VARCHAR(255) NOT NULL UNIQUE,
	name VARCHAR(255) NOT NULL
);

-- Create item table (referenced by objects_has_items)
CREATE TABLE item (
	id SERIAL PRIMARY KEY,
	kb_id VARCHAR(255) NOT NULL UNIQUE,
	name VARCHAR(255) NOT NULL,
	price INTEGER NOT NULL,
	hint TEXT,
	propbits VARCHAR(255)[]
);

-- Create object table (referenced by objects_has_items)
CREATE TABLE object (
	id SERIAL PRIMARY KEY,
	kb_id INTEGER NOT NULL UNIQUE,
	location_id INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL,
	hint TEXT,
	msg TEXT,
	CONSTRAINT fk_object_location FOREIGN KEY (location_id) REFERENCES location(id) ON DELETE CASCADE
);

-- Create junction table for objects and items
CREATE TABLE objects_has_items (
	item_id INTEGER NOT NULL,
	object_id INTEGER NOT NULL,
	profile_id INTEGER NOT NULL,
	count INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY (item_id, object_id, profile_id),
	CONSTRAINT fk_objects_has_items_item FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE,
	CONSTRAINT fk_objects_has_items_object FOREIGN KEY (object_id) REFERENCES object(id) ON DELETE CASCADE,
	CONSTRAINT fk_objects_has_items_profile FOREIGN KEY (profile_id) REFERENCES profile(id) ON DELETE CASCADE
);

-- Create indexes for foreign keys to improve query performance
CREATE INDEX idx_object_location_id ON object(location_id);
CREATE INDEX idx_objects_has_items_item_id ON objects_has_items(item_id);
CREATE INDEX idx_objects_has_items_object_id ON objects_has_items(object_id);
CREATE INDEX idx_objects_has_items_profile_id ON objects_has_items(profile_id);

-- Create indexes for kb_id columns (frequently used for lookups)
CREATE INDEX idx_item_kb_id ON item(kb_id);
CREATE INDEX idx_location_kb_id ON location(kb_id);
CREATE INDEX idx_object_kb_id ON object(kb_id);
