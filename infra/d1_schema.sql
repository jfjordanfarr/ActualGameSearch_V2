
-- Table: apps
CREATE TABLE IF NOT EXISTS apps (
	steam_appid INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	type TEXT,
	required_age INTEGER,
	is_free BOOLEAN,
	detailed_description TEXT,
	short_description TEXT,
	about_the_game TEXT,
	supported_languages TEXT,
	header_image TEXT,
	website TEXT,
	release_date TEXT,
	coming_soon BOOLEAN,
	platforms TEXT,
	metacritic_score INTEGER,
	recommendations INTEGER
	-- ... add more fields as needed
);

-- Table: app_genres
CREATE TABLE IF NOT EXISTS app_genres (
	steam_appid INTEGER,
	genre_id INTEGER,
	genre_desc TEXT,
	PRIMARY KEY (steam_appid, genre_id)
);

-- Table: app_categories
CREATE TABLE IF NOT EXISTS app_categories (
	steam_appid INTEGER,
	category_id INTEGER,
	category_desc TEXT,
	PRIMARY KEY (steam_appid, category_id)
);

-- Table: reviews
CREATE TABLE IF NOT EXISTS reviews (
	recommendationid TEXT PRIMARY KEY,
	steam_appid INTEGER,
	author_steamid TEXT,
	review TEXT,
	votes_up INTEGER,
	votes_funny INTEGER,
	voted_up BOOLEAN,
	timestamp_created INTEGER,
	language TEXT
);
