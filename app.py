from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    'node-red-connector', version='0.1.0', display_name='Node-RED',
    description=('Connect your own Node-RED runtimes to inspect and manage flows, settings, '
                 'nodes, projects and library resources through the official Admin HTTP API, '
                 'with Imperal health audits and safe deployment analysis.'),
    icon='icon.svg', capabilities=['node-red:read', 'node-red:write'],
    actions_explicit=True, system=False,
)
chat = ChatExtension(ext, tool_name='node_red', description='Node-RED Admin API connector for user-owned runtimes.')
ext.secret(
    'node_red_connections',
    'Vault-encrypted Node-RED Admin API connections. Managed by connect_node_red and never returned.',
    required=True, write_mode='both', max_bytes=65536, rotation_hint_days=90,
)(lambda: None)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get('node_red_connections')
    try: count = len(json.loads(raw)) if raw else 0
    except (TypeError, ValueError): count = 0
    return {'healthy': True, 'detail': f'{count} Node-RED runtime(s) connected.' if count else 'Not connected yet — run connect_node_red.'}

@ext.on_install
async def on_install(ctx) -> dict:
    """Give first-time users a safe, actionable connection next step."""
    return {"message": "Connect your HTTPS Node-RED Admin API runtime in the Node-RED sidebar to begin."}
