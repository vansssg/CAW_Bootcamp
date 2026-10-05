from fastapi import HTTPException, Request

from app.config import API_KEY_A, API_KEY_B

# Keys come from env (config.py). JWT_SECRET is not an API key alias — rotating
# JWT_SECRET must not silently keep a second principal-a credential.
API_KEYS = {
    API_KEY_A: "principal-a",
    API_KEY_B: "principal-b",
}

NOT_OWNER_STATUS = 404


def require_api_key(request: Request) -> str:
    key = request.headers.get("x-api-key", "").strip()
    if not key:
        raise HTTPException(status_code=401, detail="API key required")
    principal = API_KEYS.get(key)
    if principal is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    request.state.principal_id = principal
    return principal


def reject_if_not_owner(owner_id: str | None, principal_id: str) -> None:
    if owner_id != principal_id:
        raise HTTPException(status_code=NOT_OWNER_STATUS, detail="Link not found")
