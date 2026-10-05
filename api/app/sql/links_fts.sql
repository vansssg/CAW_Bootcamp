-- Postgres FTS for GET /links/search (decisions.module_08.search_strategy = db_native).
-- Table column names match module-02 seed: short_code, original_url.
-- Not applied at import: localhost:5432 is not serving; run when SEARCH_USE_POSTGRES=1.

ALTER TABLE links
  ADD COLUMN IF NOT EXISTS search_tsv tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(original_url, '') || ' ' || coalesce(short_code, ''))
  ) STORED;

CREATE INDEX IF NOT EXISTS links_search_tsv_gin ON links USING GIN (search_tsv);

-- Parameterized search (bound :owner :q :tag :limit :offset). Never concatenate q into SQL.
-- SELECT short_code, original_url, created_by AS owner, search_tsv
-- FROM links
-- WHERE created_by = :owner
--   AND (:q = '' OR search_tsv @@ plainto_tsquery('english', :q))
--   AND (:tag = '' OR :tag = ANY(tags))
-- ORDER BY created_at DESC
-- LIMIT :limit OFFSET :offset;
