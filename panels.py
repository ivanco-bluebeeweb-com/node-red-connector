"""Node-RED connector panels, compliant with UI_INTERFACE_STANDARD.md.

No decorated cards in the left sidebar. Inputs have visible labels and
contextual placeholders; setup instructions exist only in the help modal.
The one secondary App settings button is the final sidebar element.
"""
from __future__ import annotations

from imperal_sdk import ui

from app import ext
from handlers import _connections


def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings", variant="secondary", size="sm", full_width=True,
        icon="settings", on_click=ui.Call("__panel__node_red_settings"),
    )


def _connect_section() -> ui.UINode:
    return ui.Stack(direction="v", gap=3, align="stretch", children=[
        ui.Button(
            "How do I set this up?", variant="ghost", size="sm",
            icon="HelpCircle", on_click=ui.Call("__panel__node_red_help"),
        ),
        ui.Form(
            action="connect_node_red", submit_label="Verify and connect",
            children=[
                ui.Stack(direction="v", gap=1, align="stretch", children=[
                    ui.Text("Node-RED HTTPS URL", variant="caption"),
                    ui.Input(param_name="base_url", required=True,
                             placeholder="https://flows.example.com"),
                ]),
                ui.Stack(direction="v", gap=1, align="stretch", children=[
                    ui.Text("Admin API access token", variant="caption"),
                    ui.Password(param_name="access_token", required=True,
                                placeholder="Paste a Node-RED access token"),
                ]),
                ui.Stack(direction="v", gap=1, align="stretch", children=[
                    ui.Text("Environment label (optional)", variant="caption"),
                    ui.Input(param_name="label",
                             placeholder="e.g. Production automation"),
                ]),
            ],
        ),
    ])


@ext.panel("node_red_connect", slot="left", title="Node-RED", icon="🔴",
           default_width=320, min_width=260, max_width=420)
async def node_red_connect_panel(ctx, **kwargs) -> ui.UINode:
    connections = await _connections(ctx)
    connection_items: list[ui.UINode] = []
    for index, connection in enumerate(connections):
        if index:
            connection_items.append(ui.Divider())
        connection_items.append(ui.Stack(direction="v", gap=1, align="start", children=[
            ui.Text(connection.get("label") or connection.get("base_url", "Node-RED runtime")),
            ui.Text(connection.get("base_url", ""), variant="caption"),
        ]))
    children: list[ui.UINode] = [
        ui.Header(text="Node-RED", level=2,
                  subtitle="Manage your own Node-RED runtimes from Imperal"),
    ]
    if connection_items:
        children.extend([ui.Text("Connected runtimes", variant="subtitle"),
                         ui.Stack(direction="v", gap=2, align="stretch", children=connection_items),
                         ui.Divider()])
    children.extend([_connect_section(), ui.Divider(), _settings_button()])
    return ui.Stack(direction="v", gap=4, align="stretch", children=children)


@ext.panel("node_red_help", slot="center", title="How to connect Node-RED", center_overlay=True)
async def node_red_help_panel(ctx, **kwargs) -> ui.UINode:
    content = ui.Stack(direction="v", gap=3, children=[
        ui.Text("1. Enable and secure the Node-RED Admin HTTP API on your own runtime."),
        ui.Text("2. Create an access token with the read and write permissions you intend to grant."),
        ui.Text("3. Enter the public HTTPS URL and token here. The connector verifies them before saving."),
        ui.Text("4. Keep the runtime reachable from Imperal and use a TLS certificate trusted by the platform."),
        ui.Divider(),
        ui.Alert(
            title="Your runtime, your control",
            message="Imperal stores the connection Vault-encrypted and calls only your own Node-RED runtime. Token values are never displayed again.",
            type="info",
        ),
        ui.Link(label="Open official Node-RED security documentation",
                href="https://nodered.org/docs/user-guide/runtime/securing-node-red"),
    ])
    return ui.Dialog(title="How to connect Node-RED", content=content,
                     confirm_label="", cancel_label="Close")


@ext.panel("node_red_center", slot="center", title="Node-RED", icon="🔴", center_overlay=True)
async def node_red_center_panel(ctx, **kwargs) -> ui.UINode:
    return ui.Empty()
