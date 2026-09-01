from __future__ import annotations
import json
import uuid
from collections import Counter
from imperal_sdk import ActionResult
from app import chat
import node_red_client as api
from schemas import *

_SECRET = 'node_red_connections'

async def _connections(ctx) -> ActionResult:
    """Execute the typed Node-RED _connections action."""
    try: return json.loads(await ctx.secrets.get(_SECRET) or '[]')
    except (TypeError, ValueError): return []
async def _save(ctx, value) -> ActionResult: await ctx.secrets.set(_SECRET, json.dumps(value))
async def _conn(ctx, connection_id='') -> ActionResult:
    """Execute the typed Node-RED _conn action."""
    items = await _connections(ctx)
    if not items: return None, ActionResult.error('No Node-RED runtime connected yet. Use connect_node_red first.', code='NODE_RED_NOT_CONNECTED')
    item = next((x for x in items if x['id'] == connection_id), None) if connection_id else items[0]
    if not item: return None, ActionResult.error('Node-RED connection not found.', code='NODE_RED_CONNECTION_NOT_FOUND')
    return item, None
def _error(err): return ActionResult.error(err.message, code=err.code)
def _record(raw):
    return JsonRecord(id=str(raw.get('id', raw.get('name', ''))), title=str(raw.get('label', raw.get('name', raw.get('id', 'Node-RED resource')))), detail=str(raw.get('version', raw.get('type', ''))), raw=raw)
def _flow(raw):
    nodes = raw.get('nodes', []) if isinstance(raw.get('nodes'), list) else []
    return Flow(id=str(raw.get('id', '')), type=str(raw.get('type', 'tab')), label=str(raw.get('label', raw.get('name', ''))), disabled=bool(raw.get('disabled', False)), node_count=len(nodes))

@chat.function('connect_node_red', 'Connect a user-owned Node-RED runtime by verifying its HTTPS Admin API URL and access token before saving them.', action_type='write', chain_callable=True, data_model=ProviderConnection, event='node-red-connector.connect_node_red', effects=['node-red.provider.connected'])
async def connect_node_red(ctx, params: ConnectNodeRedParams) -> ActionResult:
    """Execute the typed Node-RED connect_node_red action."""
    try:
        settings = await api.verify(ctx, params.base_url, params.access_token)
        base_url = api.normalize_base_url(params.base_url)
    except api.ClientFail as err: return _error(err)
    items = await _connections(ctx)
    entry = {'id': str(uuid.uuid4()), 'base_url': base_url, 'access_token': params.access_token, 'label': params.label or base_url, 'runtime_version': str(settings.get('version', ''))}
    items.append(entry); await _save(ctx, items)
    return ActionResult.success(data=ProviderConnection(id=entry['id'], title=entry['label'], detail=base_url), summary='Node-RED runtime connected and Admin API access verified.')

@chat.function('list_connections', 'List connected Node-RED runtimes without exposing tokens.', action_type='read', chain_callable=True, data_model=ProviderConnectionList, event='node-red-connector.list_connections')
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """Execute the typed Node-RED list_connections action."""
    items = [ProviderConnection(id=x['id'], title=x.get('label', x['base_url']), detail=x['base_url']) for x in await _connections(ctx)]
    return ActionResult.success(data=ProviderConnectionList(items=items), summary=f'{len(items)} Node-RED runtime(s) connected.')

@chat.function('disconnect_node_red', 'Disconnect one Node-RED runtime by deleting only its saved access token and URL; nothing changes in Node-RED.', action_type='write', chain_callable=True, data_model=DeleteResult, event='node-red-connector.disconnect_node_red', effects=['node-red.provider.disconnected'])
async def disconnect_node_red(ctx, params: DisconnectNodeRedParams) -> ActionResult:
    """Execute the typed Node-RED disconnect_node_red action."""
    items = await _connections(ctx); kept = [x for x in items if x['id'] != params.connection_id]
    if len(kept) == len(items): return ActionResult.error('Node-RED connection not found.', code='NODE_RED_CONNECTION_NOT_FOUND')
    await _save(ctx, kept); return ActionResult.success(data=DeleteResult(ok=True, detail='Saved connection removed.'), summary='Node-RED runtime disconnected.')

@chat.function('list_flows', 'List Node-RED flow tabs from the connected runtime.', action_type='read', chain_callable=True, data_model=FlowList, event='node-red-connector.list_flows')
async def list_flows(ctx, params: ListFlowsParams) -> ActionResult:
    """Execute the typed Node-RED list_flows action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try:
        body = await api.request(ctx, conn, 'GET', '/flows')
        raw = body if isinstance(body, list) else body.get('flows', [])
        tabs = [x for x in raw if isinstance(x, dict) and x.get('type') == 'tab']
        counts = Counter(str(n.get('z', '')) for n in raw if isinstance(n, dict) and n.get('type') != 'tab')
        items = [Flow(id=str(t.get('id', '')), title=str(t.get('label', t.get('name', ''))), type='tab', label=str(t.get('label', t.get('name', ''))), disabled=bool(t.get('disabled', False)), node_count=counts.get(str(t.get('id', '')), 0)) for t in tabs]
        revision = str(body.get('rev', '')) if isinstance(body, dict) else ''
        return ActionResult.success(data=FlowList(items=items, revision=revision), summary=f'{len(items)} flow(s) found.')
    except api.ClientFail as err: return _error(err)

@chat.function('get_flow', 'Read one complete Node-RED flow by id.', action_type='read', chain_callable=True, data_model=JsonRecord, event='node-red-connector.get_flow')
async def get_flow(ctx, params: GetFlowParams) -> ActionResult:
    """Execute the typed Node-RED get_flow action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try: return ActionResult.success(data=_record(await api.request(ctx, conn, 'GET', f'/flow/{params.resource_id}')), summary='Flow loaded.')
    except api.ClientFail as err: return _error(err)

@chat.function('create_flow', 'Create a Node-RED flow from an explicit complete flow object, then deploy according to the selected deployment type.', action_type='write', chain_callable=True, data_model=JsonRecord, event='node-red-connector.create_flow', effects=['node-red.flow.created'])
async def create_flow(ctx, params: CreateFlowParams) -> ActionResult:
    """Execute the typed Node-RED create_flow action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try:
        body = await api.request(ctx, conn, 'POST', '/flow', payload=params.flow, params={'deploymentType': params.deployment_type})
        return ActionResult.success(data=_record(body if isinstance(body, dict) else params.flow), summary='Flow created; Node-RED deployment requested.')
    except api.ClientFail as err: return _error(err)

@chat.function('update_flow', 'Replace one Node-RED flow with the explicit supplied definition and deployment type.', action_type='write', chain_callable=True, data_model=JsonRecord, event='node-red-connector.update_flow', effects=['node-red.flow.updated'])
async def update_flow(ctx, params: UpdateFlowParams) -> ActionResult:
    """Execute the typed Node-RED update_flow action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try:
        body = await api.request(ctx, conn, 'PUT', f'/flow/{params.resource_id}', payload=params.flow, params={'deploymentType': params.deployment_type})
        verified = await api.request(ctx, conn, 'GET', f'/flow/{params.resource_id}')
        return ActionResult.success(data=_record(verified if isinstance(verified, dict) else body), summary='Flow updated and re-read from Node-RED for verification.')
    except api.ClientFail as err: return _error(err)

@chat.function('delete_flow', 'Permanently delete one Node-RED flow. This removes the flow from the runtime.', action_type='destructive', chain_callable=True, data_model=DeleteResult, event='node-red-connector.delete_flow', effects=['node-red.flow.deleted'])
async def delete_flow(ctx, params: DeleteFlowParams) -> ActionResult:
    """Execute the typed Node-RED delete_flow action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try:
        await api.request(ctx, conn, 'DELETE', f'/flow/{params.resource_id}')
        return ActionResult.success(data=DeleteResult(ok=True, detail=params.resource_id), summary='Flow deleted from Node-RED.')
    except api.ClientFail as err: return _error(err)

@chat.function('preview_flow_deployment', 'Analyse a proposed flow locally before writing it to Node-RED; this makes no provider changes.', action_type='read', chain_callable=True, data_model=Audit, event='node-red-connector.preview_flow_deployment')
async def preview_flow_deployment(ctx, params: FlowPreviewParams) -> ActionResult:
    """Execute the typed Node-RED preview_flow_deployment action."""
    raw = params.flow; nodes = raw.get('nodes', []) if isinstance(raw.get('nodes'), list) else []
    types = Counter(str(n.get('type', 'unknown')) for n in nodes if isinstance(n, dict))
    risky = sorted(t for t in types if any(word in t.lower() for word in ('exec', 'http request', 'mqtt out', 'email', 'function')))
    data = Audit(connection_id=params.connection_id, flow_count=1, node_type_count=len(types), risk_markers=[f'{x} ({types[x]} node(s))' for x in risky], detail='Preview only; no Node-RED write occurred.')
    return ActionResult.success(data=data, summary=f'Flow preview: {len(nodes)} node(s), {len(risky)} side-effect marker type(s).')

async def _list_records(ctx, params, path, label) -> ActionResult:
    """Execute the typed Node-RED _list_records action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try:
        body = await api.request(ctx, conn, 'GET', path); values = body if isinstance(body, list) else body.get('nodes', body.get('projects', body.get('entries', [])))
        return ActionResult.success(data=JsonRecordList(items=[_record(x) for x in values if isinstance(x, dict)]), summary=f'{len(values)} {label} found.')
    except api.ClientFail as err: return _error(err)

@chat.function('list_nodes', 'List installed Node-RED node modules and node definitions exposed by this runtime.', action_type='read', chain_callable=True, data_model=JsonRecordList, event='node-red-connector.list_nodes')
async def list_nodes(ctx, params: ListNodesParams) -> ActionResult:
    """List Node-RED modules and definitions exposed to this access token."""
    return await _list_records(ctx, params, '/nodes', 'node resource(s)')

@chat.function('list_projects', 'List Node-RED projects when projects are enabled on this runtime.', action_type='read', chain_callable=True, data_model=JsonRecordList, event='node-red-connector.list_projects')
async def list_projects(ctx, params: ListProjectsParams) -> ActionResult:
    """List Node-RED projects where the runtime has Projects API enabled."""
    return await _list_records(ctx, params, '/projects', 'project(s)')
@chat.function('get_runtime_settings', 'Read safe Node-RED runtime settings and capability metadata.', action_type='read', chain_callable=True, data_model=JsonRecord, event='node-red-connector.get_runtime_settings')
async def get_runtime_settings(ctx, params: GetSettingsParams) -> ActionResult:
    """Execute the typed Node-RED get_runtime_settings action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try: return ActionResult.success(data=_record(await api.request(ctx, conn, 'GET', '/settings')), summary='Runtime settings loaded.')
    except api.ClientFail as err: return _error(err)

@chat.function('audit_node_red_runtime', 'Build a read-only Node-RED health report: flow totals, disabled flows, node types and side-effect markers.', action_type='read', chain_callable=True, data_model=Audit, event='node-red-connector.audit_node_red_runtime')
async def audit_node_red_runtime(ctx, params: AuditParams) -> ActionResult:
    """Execute the typed Node-RED audit_node_red_runtime action."""
    conn, failure = await _conn(ctx, params.connection_id)
    if failure: return failure
    try:
        body = await api.request(ctx, conn, 'GET', '/flows')
        raw = body if isinstance(body, list) else body.get('flows', [])
        tabs = [x for x in raw if isinstance(x, dict) and x.get('type') == 'tab']
        all_nodes = [n for n in raw if isinstance(n, dict) and n.get('type') != 'tab']
        types = Counter(str(n.get('type', 'unknown')) for n in all_nodes)
        risky = sorted(t for t in types if any(word in t.lower() for word in ('exec', 'http request', 'mqtt out', 'email', 'function')))
        data = Audit(connection_id=conn['id'], flow_count=len(tabs), disabled_flow_count=sum(bool(t.get('disabled')) for t in tabs), node_type_count=len(types), risk_markers=[f'{x} ({types[x]} node(s))' for x in risky], detail='Markers identify side-effect-capable node types; they are not findings of misuse.')
        return ActionResult.success(data=data, summary=f'Audited {data.flow_count} flow(s): {data.disabled_flow_count} disabled, {data.node_type_count} node types.')
    except api.ClientFail as err: return _error(err)
