שלב הגילוי: מבינים מה הלקוח צריך.
אישור תכולה וארכיטקטורה.
תוכנית עבודה.
מימוש בעזרת AI.
בדיקה ו-review של המפתח עצמו.
אימות עצמאי של מפתח שני או של QA.
שחרור לפי רמת הסיכון.
בדיקות אחרי הפריסה.


pavel@Pavels-MBP project_inv % curl -i http://localhost:8000/health
HTTP/1.1 200 OK
date: Sun, 04 Oct 2026 19:56:18 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}%                                                                                                      pavel@Pavels-MBP project_inv % curl -i -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "bolt", "stock": 5}'
HTTP/1.1 201 Created
date: Sun, 04 Oct 2026 19:56:31 GMT
server: uvicorn
content-length: 32
content-type: application/json

{"id":1,"name":"bolt","stock":5}%                                                                                     pavel@Pavels-MBP project_inv % curl -i http://localhost:8000/items/1
HTTP/1.1 200 OK
date: Sun, 04 Oct 2026 19:56:47 GMT
server: uvicorn
content-length: 32
content-type: application/json

{"id":1,"name":"bolt","stock":5}%                                                                                     pavel@Pavels-MBP project_inv % curl -i "http://localhost:8000/items?limit=10&offset=0"
HTTP/1.1 200 OK
date: Sun, 04 Oct 2026 19:56:54 GMT
server: uvicorn
content-length: 34
content-type: application/json

[{"id":1,"name":"bolt","stock":5}]%                                                                                   pavel@Pavels-MBP project_inv % curl -i http://localhost:8000/items/999
HTTP/1.1 404 Not Found
date: Sun, 04 Oct 2026 19:57:01 GMT
server: uvicorn
content-length: 27
content-type: application/json

{"detail":"item not found"}%                                                                                          pavel@Pavels-MBP project_inv % curl -i http://localhost:8000/items/999
HTTP/1.1 404 Not Found
date: Sun, 04 Oct 2026 19:57:09 GMT
server: uvicorn
content-length: 27
content-type: application/json

{"detail":"item not found"}%                                                                                          pavel@Pavels-MBP project_inv % curl -i -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "", "stock": -3}'
HTTP/1.1 422 Unprocessable Entity
date: Sun, 04 Oct 2026 19:57:16 GMT
server: uvicorn
content-length: 274
content-type: application/json

{"detail":[{"type":"string_too_short","loc":["body","name"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}},{"type":"greater_than_equal","loc":["body","stock"],"msg":"Input should be greater than or equal to 0","input":-3,"ctx":{"ge":0}}]}%                                                                               pavel@Pavels-MBP project_inv % 

## Day 3: sending the same POST twice

Sending `POST /items` twice with the same body creates two items (ids 1 and 2).
POST is not idempotent: the server can't tell a retry from a new request.

How to prevent it: the client sends an `Idempotency-Key` header with a unique
id per logical action. The server stores the key with the response (a table with
a UNIQUE constraint on the key). A second request with the same key returns the
stored response instead of creating another row.

## Day 4: index measurement

Run: `sql/index.sql` (100,000 rows, lookup by name).

| | Plan | Execution time |
| --- | --- | --- |
| Before index | Seq Scan on items | 2.380 ms |
| After `CREATE INDEX idx_items_name` | Index Scan using idx_items_name | 0.020 ms |

The sequential scan reads every row; the index jumps straight to the match.
Price: every INSERT/UPDATE of `name` now also updates the index, and the index uses disk.

Other day 4 files: `sql/seed.sql` (made-up data), `sql/queries.sql` (ten queries),
`sql/constraints.sql` (FK, CHECK and UNIQUE violations, plus BEGIN/ROLLBACK).

## Day 6: the race test really tests

`test_concurrent_orders_do_not_oversell` sends 20 orders at once for an item
with stock 1. To prove it catches the bug, the FOR UPDATE strategy was
temporarily turned back into the naive version (plain SELECT, sleep 0.1s, write):

```
E  assert [201, 201, 20...201, 201, ...] == [201, 409, 40...409, 409, ...]
E  At index 1 diff: 201 != 409
1 failed
```

With the real code restored: all tests pass.

## Day 6: review of an AI-written delete endpoint

First draft as generated:

```python
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM items WHERE id = %s", (item_id,))
    return {"deleted": True}
```

Review comments, written before running it:

1. No `tenant_id` filter: any business can delete another business's item by id (IDOR).
2. A missing item still returns 200 `{"deleted": true}`. It should return 404; check `rowcount`.
3. If `order_items` points at the item, the foreign key makes the DELETE fail
   with an unhandled exception, so the client gets 500. It should be 409 with a clear reason.
4. Success should be 204 with no body, like the rest of the API's conventions.
5. Who may delete is not checked at all. Until auth exists (day 9) the endpoint
   is limited to TENANT_ID; once it does, only an authorized user of that tenant.

All five are fixed in `DELETE /items/{item_id}` and covered by tests in `tests/test_items.py`.
