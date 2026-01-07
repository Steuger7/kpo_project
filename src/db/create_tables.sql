CREATE TABLE users (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  username CHAR(256) UNIQUE NOT NULL,
  password CHAR(256) NOT NULL,
  book_count INTEGER DEFAULT 0
);

CREATE TABLE collection_entry (
  collection_id INTEGER NOT NULL,
  cover_i INTEGER NOT NULL,
  first_publish_year SMALLINT NOT NULL,
  key text NOT NULL,
  language CHAR(3)[] NOT NULL,
  title text NOT NULL,
  author_name TEXT[] NOT NULL,
  UNIQUE (collection_id, key)
);

ALTER TABLE collection_entry ADD CONSTRAINT fk_collection_id FOREIGN KEY (collection_id) REFERENCES users (id) ON DELETE CASCADE;

