from __future__ import annotations

from imperal_sdk import ActionResult

from app import chat
import node_red_client as api
from handlers import _conn, _error, _list_records, _record
from schemas import (
    ActivateProjectParams, DeleteLibraryEntryParams, GetProjectParams,
    InstallModuleParams, JsonRecord, JsonRecordList, LibraryEntryParams,
    ListCredentialsParams, ListLibraryParams, NodeModuleParams,
    ProjectCreateParams, UpdateRuntimeSettingsParams, WriteLibraryEntryParams,
    DeleteResult,
)


def _values(body, key: str = "") -> list[dict]:
    if isinstance(body, list):
        return [x for x in body if isinstance(x, dict)]
    if isinstance(body, dict):
        values = body.get(key, body.get("nodes", body.get("entries", [])))
        return values if isinstance(values, list) else []
    return []


@chat.function(
    "list_credentials", "List Node-RED credential definitions/metadata only. Secret credential values are never requested or returned.",
    action_type="read", chain_callable=True, data_model=JsonRecordList,
    event="node-red-connector.list_credentials",
)
async def list_credentials(ctx, params: ListCredentialsParams) -> ActionResult:
    """Execute the typed Node-RED list_credentials action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    try:
        body = await api.request(ctx, conn, "GET", "/credentials")
        return ActionResult.success(
            data=JsonRecordList(items=[_record(x) for x in _values(body, "credentials")]),
            summary="Credential metadata loaded; no credential secret values were exposed.",
        )
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "get_node_module", "Read one installed Node-RED node module's public metadata by exact module name.",
    action_type="read", chain_callable=True, data_model=JsonRecord,
    event="node-red-connector.get_node_module",
)
async def get_node_module(ctx, params: NodeModuleParams) -> ActionResult:
    """Execute the typed Node-RED get_node_module action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    try:
        body = await api.request(ctx, conn, "GET", f"/nodes/{params.module_name}")
        return ActionResult.success(data=_record(body if isinstance(body, dict) else {}), summary="Node module metadata loaded.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "install_node_module", "Install an explicit Node-RED node npm module. This changes runtime code and may require a restart/reload depending on the runtime.",
    action_type="write", chain_callable=True, data_model=JsonRecord,
    event="node-red-connector.install_node_module", effects=["node-red.module.installed"],
)
async def install_node_module(ctx, params: InstallModuleParams) -> ActionResult:
    """Execute the typed Node-RED install_node_module action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    payload = {"module": params.module_name}
    if params.version:
        payload["version"] = params.version
    try:
        body = await api.request(ctx, conn, "POST", "/nodes", payload=payload)
        return ActionResult.success(
            data=_record(body if isinstance(body, dict) else payload),
            summary="Node module install requested from Node-RED. Recheck list_nodes/runtime settings before relying on it.",
        )
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "remove_node_module", "Remove an explicit Node-RED node module. This can disable flows that use its node types.",
    action_type="destructive", chain_callable=True, data_model=DeleteResult,
    event="node-red-connector.remove_node_module", effects=["node-red.module.removed"],
)
async def remove_node_module(ctx, params: NodeModuleParams) -> ActionResult:
    """Execute the typed Node-RED remove_node_module action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    try:
        await api.request(ctx, conn, "DELETE", f"/nodes/{params.module_name}")
        return ActionResult.success(
            data=DeleteResult(ok=True, detail=params.module_name),
            summary="Node module removal requested. Inspect affected flows before redeploying them.",
        )
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "list_library_entries", "List Node-RED library entries in an explicit safe library category and path.",
    action_type="read", chain_callable=True, data_model=JsonRecordList,
    event="node-red-connector.list_library_entries",
)
async def list_library_entries(ctx, params: ListLibraryParams) -> ActionResult:
    """Execute the typed Node-RED list_library_entries action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    suffix = f"/{params.path.strip('/')}" if params.path.strip("/") else ""
    try:
        body = await api.request(ctx, conn, "GET", f"/library/{params.library_type}{suffix}")
        return ActionResult.success(data=JsonRecordList(items=[_record(x) for x in _values(body)]), summary="Library entries loaded.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "get_library_entry", "Read one explicit Node-RED library entry.", action_type="read", chain_callable=True,
    data_model=JsonRecord, event="node-red-connector.get_library_entry",
)
async def get_library_entry(ctx, params: LibraryEntryParams) -> ActionResult:
    """Execute the typed Node-RED get_library_entry action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    if not params.path.strip("/"):
        return ActionResult.error("A non-empty library entry path is required.", code="NODE_RED_LIBRARY_PATH_REQUIRED")
    try:
        body = await api.request(ctx, conn, "GET", f"/library/{params.library_type}/{params.path.strip('/')}")
        raw = body if isinstance(body, dict) else {"id": params.path, "body": body}
        return ActionResult.success(data=_record(raw), summary="Library entry loaded.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "write_library_entry", "Create or replace one explicit Node-RED library entry.", action_type="write", chain_callable=True,
    data_model=JsonRecord, event="node-red-connector.write_library_entry", effects=["node-red.library.updated"],
)
async def write_library_entry(ctx, params: WriteLibraryEntryParams) -> ActionResult:
    """Execute the typed Node-RED write_library_entry action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    if not params.path.strip("/"):
        return ActionResult.error("A non-empty library entry path is required.", code="NODE_RED_LIBRARY_PATH_REQUIRED")
    try:
        body = await api.request(ctx, conn, "PUT", f"/library/{params.library_type}/{params.path.strip('/')}", payload={"body": params.body})
        return ActionResult.success(data=_record(body if isinstance(body, dict) else {"id": params.path}), summary="Library entry saved.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "delete_library_entry", "Permanently delete one explicit Node-RED library entry.", action_type="destructive", chain_callable=True,
    data_model=DeleteResult, event="node-red-connector.delete_library_entry", effects=["node-red.library.deleted"],
)
async def delete_library_entry(ctx, params: DeleteLibraryEntryParams) -> ActionResult:
    """Execute the typed Node-RED delete_library_entry action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    if not params.path.strip("/"):
        return ActionResult.error("A non-empty library entry path is required.", code="NODE_RED_LIBRARY_PATH_REQUIRED")
    try:
        await api.request(ctx, conn, "DELETE", f"/library/{params.library_type}/{params.path.strip('/')}")
        return ActionResult.success(data=DeleteResult(ok=True, detail=params.path), summary="Library entry deleted.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "get_active_project", "Read the active Node-RED project when projects are enabled.", action_type="read", chain_callable=True,
    data_model=JsonRecord, event="node-red-connector.get_active_project",
)
async def get_active_project(ctx, params: GetProjectParams) -> ActionResult:
    """Execute the typed Node-RED get_active_project action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    try:
        body = await api.request(ctx, conn, "GET", "/project")
        return ActionResult.success(data=_record(body if isinstance(body, dict) else {}), summary="Active project loaded.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "create_project", "Create an explicit Node-RED project where the runtime exposes project management.", action_type="write", chain_callable=True,
    data_model=JsonRecord, event="node-red-connector.create_project", effects=["node-red.project.created"],
)
async def create_project(ctx, params: ProjectCreateParams) -> ActionResult:
    """Execute the typed Node-RED create_project action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    payload = {"name": params.project_name, "description": params.description}
    try:
        body = await api.request(ctx, conn, "POST", "/projects", payload=payload)
        return ActionResult.success(data=_record(body if isinstance(body, dict) else payload), summary="Project creation requested.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "activate_project", "Activate an explicit Node-RED project. This changes the runtime's active project and may reload flows.", action_type="write", chain_callable=True,
    data_model=JsonRecord, event="node-red-connector.activate_project", effects=["node-red.project.activated"],
)
async def activate_project(ctx, params: ActivateProjectParams) -> ActionResult:
    """Execute the typed Node-RED activate_project action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    try:
        body = await api.request(ctx, conn, "PUT", "/project", payload={"name": params.project_name})
        return ActionResult.success(data=_record(body if isinstance(body, dict) else {"name": params.project_name}), summary="Project activation requested; recheck active project and flows.")
    except api.ClientFail as err:
        return _error(err)


@chat.function(
    "update_runtime_settings", "Update explicit provider-supported Node-RED runtime settings. Unsupported fields are rejected by Node-RED.", action_type="write", chain_callable=True,
    data_model=JsonRecord, event="node-red-connector.update_runtime_settings", effects=["node-red.settings.updated"],
)
async def update_runtime_settings(ctx, params: UpdateRuntimeSettingsParams) -> ActionResult:
    """Execute the typed Node-RED update_runtime_settings action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure:
        return failure
    try:
        body = await api.request(ctx, conn, "PUT", "/settings", payload=params.settings)
        verified = await api.request(ctx, conn, "GET", "/settings")
        return ActionResult.success(data=_record(verified if isinstance(verified, dict) else body), summary="Runtime settings updated and re-read for verification.")
    except api.ClientFail as err:
        return _error(err)
