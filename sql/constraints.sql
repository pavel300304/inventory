-- Day 4: each statement must fail. Run with: psql -f sql/constraints.sql (no ON_ERROR_STOP)

-- foreign key: tenant 999 does not exist
INSERT INTO items (tenant_id, name, stock, sku) VALUES (999, 'ghost', 1, 'SKU-X1');

-- CHECK: stock cannot be negative
INSERT INTO items (tenant_id, name, stock, sku) VALUES (1, 'minus', -1, 'SKU-X2');

-- UNIQUE: email already used by user 1
INSERT INTO users (tenant_id, email) VALUES (1, 'dana@acme.test');

-- Transaction: delete everything, see it gone, roll back, see it back
BEGIN;
DELETE FROM order_items;
DELETE FROM items;
SELECT COUNT(*) AS items_inside_transaction FROM items;
ROLLBACK;
SELECT COUNT(*) AS items_after_rollback FROM items;
