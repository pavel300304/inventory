import asyncio
import os
import sys
import time

import httpx

ITEM_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
REQUESTS = 20


async def main():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        start = time.perf_counter()
        responses = await asyncio.gather(
            *[
                client.post("/orders", json={"item_id": ITEM_ID, "quantity": 1})
                for _ in range(REQUESTS)
            ]
        )
        elapsed = time.perf_counter() - start
    print(sorted(r.status_code for r in responses))
    print(f"{elapsed:.3f}s")


asyncio.run(main())
