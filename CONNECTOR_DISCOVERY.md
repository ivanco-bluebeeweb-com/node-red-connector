# Node-RED Connector — Connector Discovery

**Дата:** 2026-08-23
**Статус:** scope approved — maximum release

## 1. Целевой сервис и источники

Node-RED — self-hosted low-code/event-driven automation runtime. Коннектор работает с **официальным Admin HTTP API** конкретного Node-RED runtime пользователя, а не с неофициальным editor API.

Официальные источники, проверенные 2026-08-23:

- https://nodered.org/docs/api/admin/methods/
- https://nodered.org/docs/api/admin/methods/get/flows/
- https://nodered.org/docs/api/admin/methods/post/flows/
- https://nodered.org/docs/api/admin/methods/get/nodes/
- https://nodered.org/docs/api/admin/methods/get/settings/
- https://nodered.org/docs/user-guide/runtime/securing-node-red

Node-RED API availability can vary by runtime version, enabled `adminAuth`, projects configuration, installed nodes and runtime permissions. This connector discovers availability and never assumes an endpoint exists.

## 2. Карта возможностей

| Возможность Node-RED | Направление | Статус |
|---|---|---|
| Auth/token lifecycle | Both | Included |
| Runtime settings/info | Ingress | Included |
| Flows: list/get/create/update/delete | Both | Included |
| Runtime flow deployment state | Both | Included |
| Credentials metadata | Ingress | Included; secret values never read/returned |
| Installed nodes/modules | Both | Included where runtime exposes API |
| Node module install/remove | Both | Included with explicit runtime-impact warning |
| Library entries | Both | Included where runtime exposes API |
| Projects list/active/project metadata | Both | Included where runtime exposes API |
| Project create/delete/activate | Both | Included with explicit destructive/runtime gate |
| Diagnostics/runtime health | Ingress | Included as Imperal value-add |
| Flow risk, dependency and disabled-flow analysis | Ingress | Included as Imperal value-add |
| Deployment preview and verification | Both | Included as Imperal value-add |

## 3. Ярус 1 — ключевые функции

1. Multi-connection BYOK connection to a user-owned Node-RED Admin API.
2. Flow inventory, individual flow read, create/update/delete, enable/disable, and deployment-aware verification.
3. Runtime settings/version and installed node/module inventory.
4. Node-RED projects and library access where enabled by the runtime.
5. Safe, normalized errors for unsupported endpoint/version/permissions.

## 4. Ярус 2 — полное покрытие

All documented Admin API groups are addressed through typed endpoint-specific functions or a **strict allowlist** of resource/action routes. Runtime-specific capabilities are probed and reported as unavailable rather than fabricated. Credential values, editor sessions, arbitrary HTTP execution, and undocumented private endpoints are intentionally excluded for security.

## 5. Ярус 3 — Imperal value-add

- Aggregated runtime health audit.
- Flow inventory summary: enabled/disabled flows, tab count, node-type use and configuration-node dependencies.
- Risk markers for flows containing known side-effect node categories, without inspecting or exposing credentials.
- Dry-run deployment summary before flow replacement/update.
- Post-write verification: re-read resource and compare returned revision/id where available.
- Multi-connection environment separation (for example dev/stage/prod).

## 6. Решение по объёму

**Выбранная форма:** Ярус 1 + Ярус 2 + Ярус 3, maximum functionality.

**Основание:** первое сообщение пользователя от 2026-08-23: «Node-RED - разработай это приложение в максимальной форме со всеми доступными функциями с их стороны и всеми возможными функциями внутри нашего приложения для повышения эффективности». По стандарту discovery это является явным предварительным подтверждением максимального scope.

## Security boundaries

- Only HTTPS base URLs are accepted by default.
- Admin access token/password is stored only in Imperal secrets and is never returned.
- No arbitrary URL executor or raw credential read endpoint.
- Deletes, project activation, module removal and runtime-impacting writes have explicit action descriptions and require the platform confirmation gate where configured.
- Capability responses are based on the connected runtime, not assumed from documentation.
