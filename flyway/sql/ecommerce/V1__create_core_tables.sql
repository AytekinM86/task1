-- V1: core e-commerce tables (3NF).

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE addresses (
    address_id  SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    line1       VARCHAR(120) NOT NULL,
    city        VARCHAR(80) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country     VARCHAR(60) NOT NULL
);

-- Self-referencing FK lets categories form a hierarchy (parent / child).
CREATE TABLE categories (
    category_id        SERIAL PRIMARY KEY,
    name               VARCHAR(80) NOT NULL,
    parent_category_id INT REFERENCES categories(category_id)
);

CREATE TABLE products (
    product_id  SERIAL PRIMARY KEY,
    category_id INT NOT NULL REFERENCES categories(category_id),
    sku         VARCHAR(40) NOT NULL UNIQUE,
    name        VARCHAR(120) NOT NULL,
    unit_price  NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE orders (
    order_id            SERIAL PRIMARY KEY,
    customer_id         INT NOT NULL REFERENCES customers(customer_id),
    shipping_address_id INT NOT NULL REFERENCES addresses(address_id),
    placed_at           TIMESTAMP NOT NULL DEFAULT now(),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled'))
);

-- Junction resolving the many-to-many between orders and products.
-- unit_price is captured at order time (it may differ from the current product price).
CREATE TABLE order_items (
    order_id   INT NOT NULL REFERENCES orders(order_id),
    product_id INT NOT NULL REFERENCES products(product_id),
    quantity   INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id)
);

CREATE INDEX idx_addresses_customer ON addresses(customer_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
