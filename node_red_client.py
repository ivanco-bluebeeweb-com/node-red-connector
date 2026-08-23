from __future__ import annotations
import json
from urllib.parse import urlparse

class ClientFail(Exception):
    def __init__(self, message: str, code: str = 'NODE_RED_ERROR'):
        super().__init__(message)
        self.message, self.code = message, code

def normalize_base_url(value: str) -> str:
    url = value.strip().rstrip('/')
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.netloc:
        raise ClientFail('Node-RED base URL must be an absolute HTTPS URL.', 'NODE_RED_INVALID_URL')
    return url

def headers(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json', 'Content-Type': 'application/json'}

def _body(response):
    body = getattr(response, 'body', {})
    if isinstance(body, str):
        try: return json.loads(body) if body else {}
        except ValueError: return {}
    return body if isinstance(body, (dict, list)) else {}

def check(response, action: str):
    if response.status_code in (200, 201, 202, 204): return _body(response)
    if response.status_code == 401: raise ClientFail('Node-RED rejected the access token.', 'NODE_RED_TOKEN_REJECTED')
    if response.status_code == 403: raise ClientFail('The token lacks permission for this Node-RED Admin API action.', 'NODE_RED_FORBIDDEN')
    if response.status_code == 404: raise ClientFail(f'Node-RED does not expose {action} on this runtime.', 'NODE_RED_UNSUPPORTED')
    if response.status_code == 429: raise ClientFail('Node-RED rate-limited this request. Try again shortly.', 'NODE_RED_RATE_LIMITED')
    if response.status_code >= 500: raise ClientFail('Node-RED returned a server error.', 'NODE_RED_PROVIDER_ERROR')
    raise ClientFail(f'Node-RED could not complete {action} (HTTP {response.status_code}).', 'NODE_RED_REQUEST_FAILED')

async def request(ctx, conn: dict, method: str, path: str, *, payload=None, params=None):
    url = f"{conn['base_url']}{path}"
    call = getattr(ctx.http, method.lower())
    kwargs = {'headers': headers(conn['access_token']), 'params': params or {}}
    if payload is not None: kwargs['json'] = payload
    return check(await call(url, **kwargs), path)

async def verify(ctx, base_url: str, token: str) -> dict:
    conn = {'base_url': normalize_base_url(base_url), 'access_token': token}
    return await request(ctx, conn, 'GET', '/settings')
