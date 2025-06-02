from __future__ import annotations
from typing import Any, Literal as Lit, Annotated
import pydantic as pyd
from .config import Model, DefaultToolName, ModelName, PluginName


class ToolMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'tool'
    """

    id: str
    parent: str
    role: Lit['tool']
    name: DefaultToolName | PluginName
    author_metadata: AuthorMetadata | None
    create_time: float
    update_time: float | None
    status: Lit['finished_successfully', 'in_progress']
    end_turn: Lit[False] | None
    weight: float
    recipient: Lit['all', 'assistant']
    channel: None
    content: Content
    metadata: Metadata
    children: list[str]


class AuthorMetadata(Model):
    real_author: Lit['tool:web.run']


class TextContent(Model):
    content_type: Lit['text']
    text: str = pyd.Field(alias='parts')

    @pyd.model_validator(mode='before')
    @classmethod
    def convert_parts(cls, obj: Any) -> Any:
        if isinstance(obj, dict) and isinstance(obj.get('parts'), list):
            assert len(obj['parts']) == 1
            obj['parts'] = obj['parts'][0]
        return obj


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
    text: str = pyd.Field(alias='result')
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
    parts: list[TextContentPart | ImageContentPart]

    @pyd.field_validator('parts', mode='before')
    @classmethod
    def convert_text_parts(cls, parts: list) -> list:
        if any([isinstance(part, str) for part in parts]):
            # Convert string parts to TextContentPart
            return [
                {'content_type': 'text', 'text': part} if isinstance(part, str) else part
                for part in parts
            ]
        return parts


class TextContentPart(Model):
    content_type: Lit['text']
    text: str


class ImageContentPart(Model):
    content_type: Lit['image_asset_pointer']
    asset_pointer: str
    size_bytes: int
    width: int
    height: int
    fovea: int | None = None
    metadata: ImageMetadata


class ImageMetadata(Model):
    dalle: Dalle
    gizmo: None
    generation: None
    container_pixel_height: None
    container_pixel_width: None
    emu_omit_glimpse_image: None
    emu_patches_override: None
    sanitized: bool
    asset_pointer_link: None
    watermarked_asset_pointer: None


class Dalle(Model):
    gen_id: str
    prompt: str
    seed: int
    parent_gen_id: None
    edit_op: None
    serialization_title: str


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
    model_slug: ModelName | None = None
    timestamp_: Lit['absolute']
    default_model_slug: ModelName | None = None
    requested_model_slug: ModelName | None = None
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
