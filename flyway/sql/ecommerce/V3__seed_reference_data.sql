-- V3: seed sample data.

INSERT INTO customers (first_name, last_name, email) VALUES
    ('Nina',  'Patel',   'nina.patel@example.com'),
    ('Omar',  'Aliyev',  'omar.aliyev@example.com');

INSERT INTO addresses (customer_id, line1, city, postal_code, country) VALUES
    (1, '12 Maple St',  'Boston',  '02118', 'USA'),
    (2, '5 Nizami Ave', 'Baku',    'AZ1000', 'Azerbaijan');

INSERT INTO categories (name, parent_category_id) VALUES
    ('Electronics', NULL),
    ('Laptops', 1),
    ('Accessories', 1);

INSERT INTO products (category_id, sku, name, unit_price) VALUES
    (2, 'LAP-001', '14" Ultrabook',     1299.00),
    (3, 'ACC-001', 'USB-C Hub',           39.90),
    (3, 'ACC-002', 'Wireless Mouse',      24.50);

INSERT INTO orders (customer_id, shipping_address_id, placed_at, status) VALUES
    (1, 1, '2026-06-15 11:00', 'paid'),
    (2, 2, '2026-06-18 16:45', 'pending');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 1299.00),
    (1, 2, 2, 39.90),
    (2, 3, 1, 24.50);

INSERT INTO payments (order_id, amount, method, paid_at) VALUES
    (1, 1378.80, 'card', '2026-06-15 11:05');
