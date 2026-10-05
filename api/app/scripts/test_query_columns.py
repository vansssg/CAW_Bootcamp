from pathlib import Path

content = Path("app/scripts/module-02-seed-query.py").read_text()

assert "WHERE short_code = :code" in content
assert "WHERE code = :code" not in content

print("PASS: query uses short_code.")