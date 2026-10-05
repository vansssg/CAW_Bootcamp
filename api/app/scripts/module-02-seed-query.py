from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/upsk_sdf"

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    conn.execute(
        text("""
        INSERT INTO links (short_code, original_url, created_by)
        VALUES (:code, :url, :user)
        ON CONFLICT (short_code) DO NOTHING
        """),
        {
            "code": "abc123",
            "url": "https://www.example.com",
            "user": "module2",
        },
    )

    row = conn.execute(
        text("""
        SELECT short_code, original_url
        FROM links
       WHERE short_code = :code
        """),
        {"code": "abc123"},
    ).fetchone()

print(f"Inserted code: abc123")
print(f"Selected code: {row.short_code}")
print(f"Matched long_url: {row.original_url}")