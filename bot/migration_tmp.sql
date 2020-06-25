alter TABLE treehole add column type text;

create TABLE misc (
	key text unique,
	value TEXT
);

CREATE TABLE user (
	id INTEGER UNIQUE,
	card TEXT,
	nickname TEXT,
	last_speaking_timestamp INTEGER,
	last_speaking_time TEXT,
	is_kaoyan INTEGER
);