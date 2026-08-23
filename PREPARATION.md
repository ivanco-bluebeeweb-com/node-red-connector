# Node-RED Connector — Preparation

**Версия:** 0.1.0 · **Дата:** 2026-08-23
**Владелец:** Vlad / Bluebee Web · **Форма релиза:** максимум (Tier 1 + 2 + 3)

## 1. Паспорт

Node-RED Connector подключает принадлежащие пользователю Node-RED runtimes к Imperal Cloud. Он даёт наблюдаемое, безопасное управление flows, runtime settings, nodes/modules, projects и library через официальный Admin HTTP API — плюс анализ рисков и health reports внутри Imperal.

Приложение создаётся сейчас по прямому запросу на полный функционал, публичный Git, Imperal deployment, pricing и Marketplace review.

## 2. Проблема

Когда platform/automation engineer управляет несколькими Node-RED runtimes, ей приходится открывать отдельные редакторы, вручную сравнивать flows и искать причину неработающей автоматизации. Это теряет время, создаёт риск незаметного production drift и делает изменения опаснее.

Node-RED Editor хорош для построения flow, но не даёт Imperal общего контекстного слоя: multi-instance inventory, unified audit, risk summary, controlled deployment flow и cross-environment visibility.

## 3. Пользователи и jobs-to-be-done

| Роль | Цель | Критерий успеха |
|---|---|---|
| Automation engineer | Быстро понять состояние runtime и flows | За один вызов видит flow inventory, nodes и ошибки API |
| Platform owner | Управлять dev/stage/prod отдельно | Явно выбирает `connection_id`; секреты не раскрываются |
| Operations lead | Найти неактивные/рискованные flows | Получает audit с объяснимыми маркерами |
| Developer | Изменить flow безопасно | Preview, затем типизированная write-операция и reread verification |

## 4. Данные, секреты и границы

- Пользователь предоставляет URL Node-RED runtime и Admin API credential/token; они хранятся только в `ctx.secrets` в записи конкретного connection.
- В список/результаты попадают метаданные flows, но не credential values.
- Только HTTPS URLs; localhost/private networks не маскируются как «доступные» и зависят от сетевой доступности Imperal.
- API версия/permissions/features могут различаться. Не поддержанный ресурс возвращается как факт API, не выдумывается.
- Нет arbitrary URL executor, shell access, raw credential endpoint или доступа к неофициальным private editor APIs.

## 5. P0 и полный scope

### P0

1. Connect/disconnect/list multi-runtime connections.
2. Runtime settings/diagnostics and flow CRUD.
3. Nodes/modules inventory and available project/library resources.
4. Health audit, flow inventory, risk/dependency summaries.
5. Explicitly described writes with post-write readback.

### Full scope

- Admin auth capability verification.
- Flow tabs, subflows, configuration nodes and full flow collection operations.
- Node catalog and module management where officially exposed.
- Credentials metadata only.
- Projects and library CRUD where enabled.
- Runtime settings inspection and controlled settings update where exposed.
- Imperal-side audit, drift-aware deployment preview and environment separation.

## 6. UX

The primary panel is a compact runtime overview: selected connection, health, flow counts, node module count and direct actions. The left sidebar has no cards or duplicated instructions, uses dividers, and ends with exactly one secondary **App settings** button. Settings holds connection setup and disconnect together; fields always have labels and contextual placeholders, and the form container/content use full sidebar width.

## 7. Safety decisions

| Operation | Protection |
|---|---|
| Flow/project/library delete | Destructive `action_type`, unambiguous description, platform confirmation |
| Module remove/install | Runtime-impact warning and verification |
| Project activate | Explicit active project name and reread verification |
| Full flow replacement | Preview tool + post-write revision/readback |
| Secrets | Never included in entities, summaries or errors |

## 8. Quality and release gates

- Typed Pydantic params on every handler.
- Unit/scenario tests cover connection errors, unsupported endpoint, flow analysis and post-write response normalization.
- `imperal build .`, `imperal validate .`, import check and pytest are required.
- Public GitHub repository must have no secrets and a remote URL.
- Pricing is configured before deploy/review on {0,8,16,20,40,60}.
- Submit for review only after clean validation and successful deployment.

## 9. Decisions log

- 2026-08-23: user explicitly selected maximum coverage including Imperal efficiency capabilities.
- 2026-08-23: Node-RED Admin HTTP API selected as supported provider surface; version-specific routes remain capability-gated.
