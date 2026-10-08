-- Day 4: ten hand-written queries against sql/seed.sql.

-- 1. All items of one business, sorted by name
SELECT id, name, stock FROM items WHERE tenant_id = 1 ORDER BY name;

-- 2. Items with stock below 3
SELECT tenant_id, name, stock FROM items WHERE stock < 3 ORDER BY tenant_id, stock;

-- 3. Number of items per business
SELECT t.name, COUNT(i.id) AS items
FROM tenants t
LEFT JOIN items i ON i.tenant_id = t.id
GROUP BY t.name
ORDER BY t.name;

-- 4. All orders with the email of the user who placed them
SELECT o.id, o.created_at, u.email
FROM orders o
JOIN users u ON u.id = o.user_id
ORDER BY o.id;

-- 5. For each order: item names and quantities (three tables)
SELECT o.id AS order_id, i.name, oi.quantity
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN items i ON i.id = oi.item_id
ORDER BY o.id, i.name;

-- 6. Total quantity ordered of each item
SELECT i.name, SUM(oi.quantity) AS total_ordered
FROM order_items oi
JOIN items i ON i.id = oi.item_id
GROUP BY i.name
ORDER BY total_ordered DESC;

-- 7. Total stock value per business (units on the shelf)
SELECT tenant_id, SUM(stock) AS units FROM items GROUP BY tenant_id ORDER BY tenant_id;

-- 8. Items that were never ordered
SELECT i.name
FROM items i
LEFT JOIN order_items oi ON oi.item_id = i.id
WHERE oi.item_id IS NULL
ORDER BY i.name;

-- 9. Number of orders per user, including users with none
SELECT u.email, COUNT(o.id) AS orders
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.email
ORDER BY orders DESC, u.email;

-- 10. The three items with the most stock
SELECT name, stock FROM items ORDER BY stock DESC LIMIT 3;
