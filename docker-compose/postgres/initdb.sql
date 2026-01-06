-- King's Bounty Tracker Database Schema

CREATE TABLE game (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	path VARCHAR(100) NOT NULL UNIQUE,
	last_scan_time TIMESTAMP DEFAULT NULL
);
