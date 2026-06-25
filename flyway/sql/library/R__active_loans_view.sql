-- Repeatable migration: aktiv və gecikmiş borcları göstərir.
-- days_remaining: neçə gün qalıb (mənfi = gecikib)

CREATE OR REPLACE VIEW active_loans AS
SELECT l.loan_id,
       l.loaned_at,
       l.due_at,
       l.status,
       m.first_name || ' ' || m.last_name          AS member_name,
       m.membership_type,
       b.title                                      AS book_title,
       b.isbn,
       g.name                                       AS genre,
       EXTRACT(DAY FROM (l.due_at - now()))::INT    AS days_remaining
FROM loans l
JOIN members m ON m.member_id = l.member_id
JOIN books   b ON b.book_id   = l.book_id
JOIN genres  g ON g.genre_id  = b.genre_id
WHERE l.status IN ('active', 'overdue')
ORDER BY l.due_at;
