CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR NOT NULL,
	password VARCHAR NOT NULL
);

CREATE TABLE books (
    isbn VARCHAR PRIMARY KEY NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    review_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id VARCHAR REFERENCES books,
    poster INTEGER REFERENCES users,
    review VARCHAR NOT NULL
);