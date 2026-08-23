# Node-RED Connector — Scenario Tests

**Дата:** 2026-08-23
**Статус:** offline contract scenarios; live-provider scenarios require a user-owned Node-RED Admin API runtime.

## Personas and data classes

- **Automation engineer:** reads runtime and flow inventory before a controlled edit.
- **Platform owner:** manages separate Production and Staging connections.
- **Operations lead:** uses an audit to locate disabled flows and side-effect-capable node types.

Data classes: no connection, invalid HTTP URL, rejected token, authorised read-only token, full Admin API token, runtime without optional Projects/Library API.

## Given–When–Then scenarios

1. **First connection — happy path**
   - Given an HTTPS runtime URL and valid Admin API token,
   - When `connect_node_red` verifies `/settings`,
   - Then credentials are saved only in `node_red_connections` and the response exposes only connection metadata.

2. **Unsafe URL rejection**
   - Given an `http://` URL,
   - When a connection is attempted,
   - Then the client rejects it before an API request with `NODE_RED_INVALID_URL`.

3. **Authorization failure**
   - Given an expired/revoked token,
   - When Node-RED returns HTTP 401,
   - Then the user gets `NODE_RED_TOKEN_REJECTED`; the token is never echoed.

4. **Optional API unavailable**
   - Given a runtime without Projects or Library API,
   - When a related read is requested,
   - Then Node-RED's 404 becomes `NODE_RED_UNSUPPORTED`, not fabricated empty data.

5. **Flow write safety**
   - Given an intended create/update,
   - When the engineer calls `preview_flow_deployment`,
   - Then the connector returns node count and side-effect-capable type markers without writing.
   - When an explicit create/update follows,
   - Then the selected deployment type is sent to Node-RED and the provider result is returned.

6. **Destructive/runtime-impacting actions**
   - Given an explicit flow/module/library deletion or project activation,
   - When the action is invoked,
   - Then the platform uses the action's destructive classification and the connector does not substitute a broad/bulk deletion.

7. **Connection isolation**
   - Given Production and Staging connections,
   - When an explicit `connection_id` is supplied,
   - Then requests use only that saved URL/token pair.

## Offline results

`tests/test_node_red_client.py` covers URL normalization, HTTP error mapping and success-body parsing. SDK build/import/validation are run independently in the release checklist.

## Live gate

A live smoke test is intentionally deferred until a user-owned runtime and least-privilege Admin API token are connected. No fake success is recorded for this gate.
