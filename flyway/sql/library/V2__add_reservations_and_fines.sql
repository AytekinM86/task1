-- V2: reservations (kitab sıraya qoyma) və fines (cərimələr) əlavə edilir.

CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    book_id        INT NOT NULL REFERENCES books(book_id),
    member_id      INT NOT NULL REFERENCES members(member_id),
    reserved_at    TIMESTAMP NOT NULL DEFAULT now(),
    expires_at     TIMESTAMP NOT NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending', 'fulfilled', 'cancelled', 'expired'))
);

CREATE TABLE fines (
    fine_id   SERIAL PRIMARY KEY,
    loan_id   INT NOT NULL REFERENCES loans(loan_id),
    amount    NUMERIC(8,2) NOT NULL CHECK (amount > 0),
    reason    VARCHAR(60) NOT NULL
              CHECK (reason IN ('overdue', 'lost', 'damaged')),
    issued_at TIMESTAMP NOT NULL DEFAULT now(),
    paid_at   TIMESTAMP
);

CREATE INDEX idx_reservations_book   ON reservations(book_id);
CREATE INDEX idx_reservations_member ON reservations(member_id);
CREATE INDEX idx_fines_loan          ON fines(loan_id);
