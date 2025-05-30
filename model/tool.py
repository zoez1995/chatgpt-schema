from __future__ import annotations
from typing import Literal as Lit, Annotated
import pydantic as pyd
from .config import Model, DefaultToolName, PluginName


class ToolMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'tool'
    """

    id: str
    role: Lit['tool']
    author: Author
    create_time: float
    update_time: float | None
    content: Content
    status: Lit['finished_successfully', 'in_progress']
    end_turn: Lit[False] | None
    weight: float
    metadata: Metadata
    recipient: Lit['all', 'assistant']
    channel: None


class Author(Model):
    role: Lit['tool']
    name: DefaultToolName | PluginName
    metadata: AuthorMetadata | None


class AuthorMetadata(Model):
    real_author: Lit['tool:web.run']


class TextContent(Model):
    content_type: Lit['text']
    parts: list[str]


class CodeContent(Model):
    content_type: Lit['code']
    language: str
    text: str
    response_format_name: None


class ErrorContent(Model):
    content_type: Lit['system_error']
    name: str
    text: str


class ExecutionOutputContent(Model):
    content_type: Lit['execution_output']
    text: str


class BrowserDisplayContent(Model):
    content_type: Lit['tether_browsing_display']
    result: str
    summary: str | None
    assets: Lit[[], None]  # type:ignore
    tether_id: None = None


class BrowserQuoteContent(Model):
    content_type: Lit['tether_quote']
    url: str
    domain: str
    text: str
    title: str
    tether_id: None = None


class MultimodalTextContent(Model):
    content_type: Lit['multimodal_text']
    parts: list[str | ImageContentPart]


class ImageContentPart(Model):
    content_type: Lit['image_asset_pointer']
    asset_pointer: str
    size_bytes: int
    width: int
    height: int
    fovea: int | None = None
    metadata: dict


type Content = Annotated[
    TextContent
    | ErrorContent
    | CodeContent
    | ExecutionOutputContent
    | BrowserDisplayContent
    | BrowserQuoteContent
    | MultimodalTextContent,
    pyd.Discriminator('content_type'),
]


class Metadata(Model):
    message_type: None
    model_slug: str | None = None
    timestamp_: Lit['absolute']
    default_model_slug: str | None = None
    requested_model_slug: str | None = None
    parent_id: str | None = None
    request_id: str | None = None
    is_complete: bool | None = None
    aggregate_result: dict | None = None
    cite_metadata: dict | None = pyd.Field(None, alias='_cite_metadata')
    status: Lit['finished', 'failed'] | None = None
    is_visually_hidden_from_conversation: Lit[True] | None = None
    pad: str | None = None
    jit_plugin_data: dict | None = None
    gizmo_id: str | None = None
    voice_mode_message: bool | None = None
    reasoning_status: Lit['is_reasoning'] | None = None
    debug_sonic_thread_id: str | None = None
    initial_text: str | None = None
    finished_duration_sec: int | None = None
    finished_text: str | None = None
    cloud_doc_urls: list[None] | None = None
    command: Command | None = None
    args: list[str] | list[int] | list[list[int]] | None = None
    kwargs: MetadataKwargs | None = None
    finish_details: FinishDetails | None = None
    invoked_plugin: InvokedPlugin | None = None
    search_result_groups: list[SearchResultGroup] | None = None
    ada_visualizations: list[Visualization] | None = None
    canvas: Canvas | None = None


class SearchResultGroup(Model):
    type: Lit['search_result_group']
    domain: str
    entries: list[SearchResultEntry]


class SearchResultEntry(Model):
    type: Lit['search_result']
    url: str
    title: str
    snippet: str
    ref_id: None
    pub_date: float | None
    attribution: str


class VisualizationTable(Model):
    type: Lit['table']
    file_id: str
    title: str


class VisualizationChart(Model):
    type: Lit['chart']
    file_id: str | None = None
    title: str | None = None
    chart_type: Lit['bar']
    fallback_to_image: Lit[False]


type Visualization = Annotated[
    VisualizationTable | VisualizationChart,
    pyd.Discriminator('type'),
]


class Canvas(Model):
    textdoc_id: str
    textdoc_type: Lit['document', 'code/python']
    version: Lit[1]
    title: str
    create_source: Lit['model']


class MetadataKwargs(Model):
    message_id: str
    pending_message_id: str | None = None
    sync_write: Lit[False] | None = None


type Command = Lit[
    'search',
    'mclick',
    'click',
    'quote_lines',
    'back',
    'quote',
    'open_url',
    'scroll',
    'context_stuff',
    'create_textdoc',
]


class FinishDetails(Model):
    type: Lit['interrupted']


class InvokedPlugin(Model):
    type: Lit['remote']
    namespace: str
    plugin_id: str
    http_response_status: int


# Keep at end of file
ToolMessage.model_rebuild()
