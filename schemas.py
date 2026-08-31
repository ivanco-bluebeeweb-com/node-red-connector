from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from imperal_sdk import sdl

class NoParams(BaseModel): pass
class Conn(BaseModel):
    connection_id: str = Field('', description='Connection id from list_connections; omit only when one connection exists.')
class Resource(Conn):
    resource_id: str = Field(..., description='Node-RED resource id.')
class ProviderConnection(sdl.Entity):
    id: str = ''
    title: str = ''
    detail: str = ''
class ProviderConnectionList(sdl.Entity):
    id: str = ''
    title: str = ''
    items: list[ProviderConnection] = []
class DeleteResult(sdl.Entity):
    id: str = ''
    title: str = ''
    ok: bool = True
    detail: str = ''

class ConnectNodeRedParams(BaseModel):
    base_url: str = Field(..., description='HTTPS Node-RED editor/admin URL, e.g. https://flows.example.com.')
    access_token: str = Field(..., description='Node-RED Admin API access token with required permissions.')
    label: str = Field('', description='Friendly environment label, e.g. Production.')
class DisconnectNodeRedParams(BaseModel): connection_id: str

class Flow(sdl.Entity):
    id: str = ''
    title: str = ''
    type: str = ''
    label: str = ''
    disabled: bool = False
    node_count: int = 0
class FlowList(sdl.Entity):
    id: str = ''
    title: str = ''
    items: list[Flow] = []
    revision: str = ''
class GetFlowParams(Resource): pass
class ListFlowsParams(Conn): pass
class CreateFlowParams(Conn):
    flow: dict[str, Any] = Field(..., description='Complete Node-RED flow object, with explicit id/type/label/nodes fields.')
    deployment_type: str = Field('flows', pattern='^(nodes|flows|full|reload)$', description='Node-RED deployment type.')
class UpdateFlowParams(Resource):
    flow: dict[str, Any] = Field(..., description='Complete replacement flow object from get_flow, edited explicitly.')
    deployment_type: str = Field('flows', pattern='^(nodes|flows|full|reload)$')
class DeleteFlowParams(Resource): pass
class FlowPreviewParams(Conn):
    flow: dict[str, Any] = Field(..., description='Proposed flow to analyse only; no provider write occurs.')

class JsonRecord(sdl.Entity):
    id: str = ''
    title: str = ''
    detail: str = ''
    raw: dict[str, Any] = Field(default_factory=dict)
class JsonRecordList(sdl.Entity):
    id: str = ''
    title: str = ''
    items: list[JsonRecord] = []
class ListNodesParams(Conn): pass
class ListProjectsParams(Conn): pass
class ListLibraryParams(Conn):
    library_type: str = Field('flows', pattern='^(flows|functions|templates)$')
    path: str = Field('', description='Optional library path.')
class GetSettingsParams(Conn): pass
class UpdateSettingsParams(Conn):
    settings: dict[str, Any] = Field(..., description='Explicit provider-supported settings fields only.')

class ModuleActionParams(Conn):
    module: str = Field(..., pattern=r'^node-red-[A-Za-z0-9._-]+$', description='Exact Node-RED module package name.')
class ProjectActionParams(Conn):
    project_name: str = Field(..., min_length=1, max_length=120)
class ProjectCreateParams(ProjectActionParams):
    description: str = Field('', max_length=500)

class Audit(sdl.Entity):
    id: str = ''
    title: str = ''
    connection_id: str = ''
    flow_count: int = 0
    disabled_flow_count: int = 0
    node_type_count: int = 0
    risk_markers: list[str] = Field(default_factory=list)
    detail: str = ''
class AuditParams(Conn): pass

class ListCredentialsParams(Conn): pass
class NodeModuleParams(Conn):
    module_name: str = Field(..., min_length=1, max_length=200, description='Exact installed Node-RED module name from list_nodes.')
class InstallModuleParams(Conn):
    module_name: str = Field(..., pattern=r'^(?:@[-A-Za-z0-9._]+/)?node-red-[A-Za-z0-9._-]+$', description='Exact npm package name for the Node-RED node module.')
    version: str = Field('', max_length=100, description='Optional exact npm package version; omit for the provider default.')
class LibraryEntryParams(Conn):
    library_type: str = Field('flows', pattern='^(flows|functions|templates)$', description='Node-RED library category.')
    path: str = Field('', max_length=500, description='Library entry path relative to its category.')
class WriteLibraryEntryParams(LibraryEntryParams):
    body: str = Field(..., max_length=500000, description='Complete text content for this library entry.')
class DeleteLibraryEntryParams(LibraryEntryParams): pass
class GetProjectParams(ProjectActionParams): pass
class ActivateProjectParams(ProjectActionParams): pass
class UpdateRuntimeSettingsParams(UpdateSettingsParams): pass
