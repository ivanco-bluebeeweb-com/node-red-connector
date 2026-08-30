# Node-RED Connector — UI component plan

Источники: `Docs/session-notes/UI_COMPONENT_VOCABULARY.md`, `UI_INTERFACE_STANDARD.md`,
`concepts/panels.md`. Основано на `POST_CONNECT_EXPERIENCE.md` этого приложения.

## 1. Компоненты

| Экран | Примитивы | Почему именно эти |
|---|---|---|
| Sidebar (left) | `ui.Column`(align="start") + `ui.Text`(instance URL) + `ui.Divider` + navigation `ui.ListItem`(Flows/Nodes/Deployments) + `ui.Button`("App settings") | Без карточек по стандарту. |
| Flow List (center, `center_overlay=True`) | `ui.Stats`(Active flows/Disabled/Nodes total) + `ui.DataTable`(name/tab label, enabled Toggle-колонка editable, nodes count; sortable) | Активация/деактивация flow (tab) прямо из таблицы через editable toggle-колонку. |
| Flow Detail | Back-button + `ui.KeyValue`(tab id/nodes count) + `ui.Graph`(nodes=Node-RED nodes, edges=wires — реальная топология flow) + `ui.Button`("Deploy") | `Graph` (Cytoscape.js) — единственный примитив, подходящий для визуализации графа nodes+wires Node-RED flow. |
| Node Detail (в рамках flow) | `ui.KeyValue`(type/config properties) | Просмотр параметров конкретного node внутри flow. |
| Deployment History | `ui.DataTable`(deployed_at, user, flows count; sortable) | Табличная история деплоев конфигурации Node-RED. |
| Debug Log Viewer | `ui.Code`(language="json", debug sidebar messages, readonly) | `Code`(json) — моноширинный вывод debug-сообщений из debug node. |
| Deploy Confirmation | `ui.Dialog`(title="Задеплоить flow?", content=`ui.Text`("Изменения будут применены к работающему runtime немедленно."), confirm_label="Задеплоить") | Deploy применяется к живому runtime — обязателен `Dialog` с подтверждением. |
| App Settings | `ui.Accordion`([Connections+Disconnect, Instance URL/Admin Auth Config]) | Централизованные настройки по стандарту. |

## 2. User flow (валидно по panel lifecycle)

1. **SESSION INIT** → `__panel__nodered_sidebar` рендерит instance + разделы,
   `auto_action` открывает Flow List с текущими enabled/disabled статусами табов.
2. Flow List: editable toggle "enabled" → `on_cell_edit` вызывает `set_flow_state`
   напрямую (обратимо, не требует полного deploy) → `refresh_panels`.
3. Клик на строку flow → Flow Detail — `Graph` рендерит nodes+wires топологию.
4. "Deploy" → `ui.Dialog` подтверждение → `ui.Call("deploy_flows")` →
   `refresh_panels` + запись в Deployment History.
5. Debug Log Viewer доступен из Flow Detail или отдельным пунктом сайдбара.
6. App Settings — только через кнопку в сайдбаре, единственное место с disconnect.

## 3. Экраны/карточки (артефакты для реализации)

- `panels.py`: `__panel__nodered_sidebar` (left).
- `panels_flows.py`: `__panel__flow_list` (center, `center_overlay=True`,
  editable toggle), `__panel__flow_detail` (center, параметризован `flow_id`, Graph).
- `panels_deployments.py`: `__panel__deployment_history` (center).
- `panels_debug.py`: `__panel__debug_log` (center, Code json).
- `panels_settings.py`: `__panel__app_settings` (center overlay, Accordion,
  единственное место с disconnect).
