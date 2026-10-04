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