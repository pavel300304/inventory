-- Day 4: made-up data. Two businesses, two users each, five items each, three orders.
INSERT INTO tenants (id, name) VALUES
  (1, 'Acme Hardware'),
  (2, 'Best Tools');

INSERT INTO users (id, tenant_id, email) VALUES
  (1, 1, 'dana@acme.test'),
  (2, 1, 'yossi@acme.test'),
  (3, 2, 'noa@best.test'),
  (4, 2, 'omer@best.test');

INSERT INTO items (id, tenant_id, name, stock, sku) VALUES
  (1,  1, 'bolt',        50, 'SKU-1'),
  (2,  1, 'nut',        120, 'SKU-2'),
  (3,  1, 'washer',       2, 'SKU-3'),
  (4,  1, 'screw',      200, 'SKU-4'),
  (5,  1, 'anchor',       1, 'SKU-5'),
  (6,  2, 'hammer',      10, 'SKU-6'),
  (7,  2, 'saw',          4, 'SKU-7'),
  (8,  2, 'drill',        0, 'SKU-8'),
  (9,  2, 'tape',        30, 'SKU-9'),
  (10, 2, 'level',        2, 'SKU-10');

INSERT INTO orders (id, tenant_id, user_id) VALUES
  (1, 1, 1),
  (2, 1, 2),
  (3, 2, 3);

INSERT INTO order_items (order_id, item_id, quantity) VALUES
  (1, 1, 10),
  (1, 2, 20),
  (2, 1, 5),
  (2, 3, 1),
  (3, 6, 2),
  (3, 9, 3);

-- explicit ids above, so move the sequences past them
SELECT setval('tenants_id_seq', 2);
SELECT setval('users_id_seq', 4);
SELECT setval('items_id_seq', 10);
SELECT setval('orders_id_seq', 3);
