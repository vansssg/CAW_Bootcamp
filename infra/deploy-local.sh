#!/usr/bin/env bash
# Local fallback deploy (Module 08). Requires a running Docker daemon.
# Usage: IMAGE_TAG=<git sha> ./infra/deploy-local.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD)}"
export IMAGE_TAG="$TAG"
echo "deploy IMAGE_TAG=$IMAGE_TAG (names only; no secret values printed)"
docker compose -f infra/docker-compose.yml up -d --build app
echo "rollback: IMAGE_TAG=<previous_sha> docker compose -f infra/docker-compose.yml up -d app"
