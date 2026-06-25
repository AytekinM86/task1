-- Domain: Library Management System
-- Entities: genres, authors, books, book_authors, members, loans

CREATE TABLE genres (
    genre_id    SERIAL PRIMARY KEY,
    name        VARCHAR(80) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE authors (
    author_id   SERIAL PRIMARY KEY,
    first_name  VARCHAR(60) NOT NULL,
    last_name   VARCHAR(60) NOT NULL,
    birth_year  SMALLINT,
    nationality VARCHAR(60)
);

CREATE TABLE books (
    book_id          SERIAL PRIMARY KEY,
    isbn             VARCHAR(20) NOT NULL UNIQUE,
    title            VARCHAR(200) NOT NULL,
    genre_id         INT NOT NULL REFERENCES genres(genre_id),
    published_year   SMALLINT,
    total_copies     SMALLINT NOT NULL DEFAULT 1 CHECK (total_copies >= 1),
    available_copies SMALLINT NOT NULL DEFAULT 1 CHECK (available_copies >= 0),
    created_at       TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE book_authors (
    book_id   INT NOT NULL REFERENCES books(book_id),
    author_id INT NOT NULL REFERENCES authors(author_id),
    role      VARCHAR(40) NOT NULL DEFAULT 'author'
              CHECK (role IN ('author', 'co-author', 'editor', 'translator')),
    PRIMARY KEY (book_id, author_id)
);

CREATE TABLE members (
    member_id       SERIAL PRIMARY KEY,
    first_name      VARCHAR(60) NOT NULL,
    last_name       VARCHAR(60) NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    membership_type VARCHAR(20) NOT NULL DEFAULT 'standard'
                    CHECK (membership_type IN ('standard', 'student', 'senior', 'premium')),
    joined_at       DATE NOT NULL DEFAULT CURRENT_DATE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE loans (
    loan_id     SERIAL PRIMARY KEY,
    book_id     INT NOT NULL REFERENCES books(book_id),
    member_id   INT NOT NULL REFERENCES members(member_id),
    loaned_at   TIMESTAMP NOT NULL DEFAULT now(),
    due_at      TIMESTAMP NOT NULL,
    returned_at TIMESTAMP,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'returned', 'overdue', 'lost'))
);

CREATE INDEX idx_books_genre         ON books(genre_id);
CREATE INDEX idx_book_authors_book   ON book_authors(book_id);
CREATE INDEX idx_book_authors_author ON book_authors(author_id);
CREATE INDEX idx_loans_book          ON loans(book_id);
CREATE INDEX idx_loans_member        ON loans(member_id);
