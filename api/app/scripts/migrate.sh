#!/bin/sh
# One-off schema apply. Not part of uvicorn CMD.
# Rollback of a failed migration: restore DB snapshot, then redeploy previous IMAGE_TAG.
# Do not alembic downgrade on a DB that already took writes.
set -euo pipefail
cd "$(dirname "$0")/../.."
alembic upgrade head
