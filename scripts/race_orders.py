import asyncio
import sys

import httpx

ITEM_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
REQUESTS = 20


async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        responses = await asyncio.gather(
            *[
                client.post("/orders", json={"item_id": ITEM_ID, "quantity": 1})
                for _ in range(REQUESTS)
            ]
        )
    print(sorted(r.status_code for r in responses))


asyncio.run(main())
