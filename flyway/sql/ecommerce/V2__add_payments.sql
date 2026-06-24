-- V2: incremental change — add payments against orders.

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id   INT NOT NULL REFERENCES orders(order_id),
    amount     NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    method     VARCHAR(20) NOT NULL
               CHECK (method IN ('card', 'paypal', 'bank_transfer', 'cash_on_delivery')),
    paid_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_payments_order ON payments(order_id);
