from app.db import get_conn

BATCH_SIZE = 1000


def main():
    total = 0
    while True:
        with get_conn() as conn:
            result = conn.execute(
                """
                UPDATE items
                SET sku = 'SKU-' || id
                WHERE id IN (
                    SELECT id FROM items WHERE sku IS NULL LIMIT %s
                )
                """,
                (BATCH_SIZE,),
            )
            updated = result.rowcount
        total += updated
        print(f"updated {updated} rows, {total} in total")
        if updated == 0:
            break


if __name__ == "__main__":
    main()
