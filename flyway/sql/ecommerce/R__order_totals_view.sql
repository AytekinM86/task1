-- Repeatable migration (R__): order totals derived from order_items.
-- Re-applied by Flyway whenever this file's checksum changes.

CREATE OR REPLACE VIEW order_totals AS
SELECT o.order_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       o.status,
       o.placed_at,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN customers   c  ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
GROUP BY o.order_id, customer_name, o.status, o.placed_at
ORDER BY o.order_id;
