-- Orderly analytical queries.
-- Each query is introduced by a marker comment of the form:
--   -- @query: <name>
-- The test suite extracts queries by marker and runs them against the seed
-- database. Keep one statement per query.

-- @query: category_totals
-- Revenue per product category, completed orders only, highest first.
SELECT p.category,
       SUM(oi.qty * oi.unit_price) AS revenue
FROM order_items oi
JOIN orders   o ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY revenue DESC;

-- @query: monthly_revenue
SELECT strftime('%Y-%m', o.order_date) AS month,
       SUM(oi.qty * oi.unit_price) AS revenue,
       COUNT(DISTINCT o.id) AS order_count
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.status = 'completed'
GROUP BY month
ORDER BY month;
-- @query: top_products_per_month
WITH sales AS (
    SELECT strftime('%Y-%m', o.order_date) AS month,
           p.name AS product,
           SUM(oi.qty) AS total_qty
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON p.id = oi.product_id
    WHERE o.status = 'completed'
    GROUP BY month, product
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY month
               ORDER BY total_qty DESC, product
           ) AS rnk
    FROM sales
)
SELECT month, product, total_qty, rnk
FROM ranked
WHERE rnk <= 2
ORDER BY month, rnk;

-- @query: customers_without_orders
-- TODO(T3-Q3): customers who have NEVER placed a completed order.
-- Use NOT EXISTS or NOT IN. Expected columns: name, city  (ordered by name)
SELECT 
    c.name,
    c.city
FROM customers c
WHERE NOT EXISTS (
    SELECT 1        
    FROM orders o
    WHERE o.customer_id = c.id AND o.status = 'completed'
)
ORDER BY c.name;    
