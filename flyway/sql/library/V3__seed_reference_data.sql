-- V3: hər cədvələ ən az 3 nümunə məlumat daxil edilir.

INSERT INTO genres (name, description) VALUES
    ('Fiction',         'Narrative works not based on fact'),
    ('Science Fiction', 'Speculative fiction involving science and technology'),
    ('Classic',         'Timeless works of literary significance');

INSERT INTO authors (first_name, last_name, birth_year, nationality) VALUES
    ('George', 'Orwell', 1903, 'British'),
    ('Isaac',  'Asimov', 1920, 'American'),
    ('Jane',   'Austen', 1775, 'British');

INSERT INTO books (isbn, title, genre_id, published_year, total_copies, available_copies) VALUES
    ('978-0451524935', 'Nineteen Eighty-Four', 3, 1949, 4, 3),
    ('978-0553293357', 'Foundation',           2, 1951, 3, 3),
    ('978-0141439518', 'Pride and Prejudice',  3, 1813, 5, 5);

INSERT INTO book_authors (book_id, author_id, role) VALUES
    (1, 1, 'author'),
    (2, 2, 'author'),
    (3, 3, 'author');

INSERT INTO members (first_name, last_name, email, phone, membership_type, joined_at) VALUES
    ('Alice', 'Walker', 'alice.walker@example.com', '+1-555-0201', 'standard', '2025-01-15'),
    ('Ben',   'Nguyen', 'ben.nguyen@example.com',   '+1-555-0202', 'student',  '2025-03-22'),
    ('Clara', 'Osei',   'clara.osei@example.com',   '+1-555-0203', 'premium',  '2024-11-10');

INSERT INTO loans (book_id, member_id, loaned_at, due_at, returned_at, status) VALUES
    (1, 1, '2026-06-01 10:00', '2026-06-15 10:00', '2026-06-14 09:30', 'returned'),
    (2, 2, '2026-06-10 11:00', '2026-06-24 11:00', NULL,               'active'),
    (3, 3, '2026-05-20 14:00', '2026-06-03 14:00', NULL,               'overdue');

INSERT INTO reservations (book_id, member_id, reserved_at, expires_at, status) VALUES
    (1, 2, '2026-06-15 12:00', '2026-06-22 12:00', 'pending'),
    (3, 1, '2026-06-16 09:00', '2026-06-23 09:00', 'pending'),
    (2, 3, '2026-06-17 08:00', '2026-06-24 08:00', 'cancelled');

INSERT INTO fines (loan_id, amount, reason, issued_at) VALUES
    (3, 2.50, 'overdue', '2026-06-04 09:00'),
    (3, 2.50, 'overdue', '2026-06-05 09:00'),
    (3, 2.50, 'overdue', '2026-06-06 09:00');
