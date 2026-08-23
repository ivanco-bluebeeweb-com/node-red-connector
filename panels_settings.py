"""Single App settings screen for Node-RED connection management."""
from __future__ import annotations

from imperal_sdk import ui

from app import ext
from handlers import _connections


def _connection_row(connection: dict) -> ui.UINode:
    label = connection.get("label") or connection.get("base_url", "Node-RED runtime")
    return ui.Stack(direction="v", gap=1, align="start", children=[
        ui.Text(label, variant="body"),
        ui.Text(connection.get("base_url", ""), variant="caption"),
        ui.Button(
            "Disconnect", variant="danger", size="sm",
            on_click=ui.Call("disconnect_node_red", connection_id=connection.get("id", "")),
        ),
    ])


@ext.panel("node_red_settings", slot="center", title="Node-RED settings")
async def node_red_settings_panel(ctx, **kwargs) -> ui.UINode:
    connections = await _connections(ctx)
    if not connections:
        return ui.Stack(direction="v", gap=2, align="start", children=[
            ui.Text("Connections", variant="heading"),
            ui.Text("No Node-RED runtime connected yet.", variant="caption"),
        ])
    rows: list[ui.UINode] = [ui.Text("Connections", variant="heading")]
    for index, connection in enumerate(connections):
        if index:
            rows.append(ui.Divider())
        rows.append(_connection_row(connection))
    return ui.Stack(direction="v", gap=2, align="start", children=rows)
