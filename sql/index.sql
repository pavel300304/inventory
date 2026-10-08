-- Day 4: measure a name lookup on 100,000 rows, before and after an index.
INSERT INTO items (tenant_id, name, stock, sku)
SELECT 1, 'item-' || g, 10, 'SKU-G' || g FROM generate_series(1, 100000) g;
ANALYZE items;

EXPLAIN ANALYZE SELECT * FROM items WHERE name = 'item-77777';

CREATE INDEX idx_items_name ON items (name);

EXPLAIN ANALYZE SELECT * FROM items WHERE name = 'item-77777';
