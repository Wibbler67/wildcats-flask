DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS fixtures;
DROP TABLE IF EXISTS availabilities;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS subs;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  is_admin INTEGER
);

CREATE TABLE fixtures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  fixture_date DATE NOT NULL,
  fixture_day DAY NOT NULL,
  match_type TEXT NOT NULL,
  team TEXT NOT NULL,
  location TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE availabilities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  attendee_id INTEGER NOT NULL,
  fixture_id INTEGER NOT NULL,
  availability INTEGER NOT NULL,
  FOREIGN KEY (attendee_id) REFERENCES user (id),
  FOREIGN KEY (fixture_id) REFERENCES fixtures (id)
);

CREATE TABLE results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fixture_id INTEGER NOT NULL,
  wildcat_legs INTEGER NOT NULL,
  opposition_legs INTEGER NOT NULL,
  result varchar(1),
  FOREIGN KEY (fixture_id) REFERENCES fixtures (id)
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE subs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  attendee_id INTEGER NOT NULL,
  fixture_id INTEGER NOT NULL,
  amount_paid INTEGER NOT NULL,
  FOREIGN KEY (attendee_id) REFERENCES user (id),
  FOREIGN KEY (fixture_id) REFERENCES fixtures (id)
);