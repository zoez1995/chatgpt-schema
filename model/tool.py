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
    end_turn: bool | None
    weight: float
    recipient: Lit['all', 'assistant']
    channel: Lit['commentary'] | None = None
    content: Content
    metadata: Metadata
    children: list[str]


class AuthorMetadata(Model):
    real_author: Lit['tool:web.run','tool:web', 'tool:web.search']
    sonicberry_model_id: Lit['current_sonicberry_paid', 'alpha.sonicberry_2s_p'] | None = None
    source: Lit['sonic_tool'] | None = None



class TextContent(Model):
    content_type: Lit['text']
    text: str = pyd.Field(alias='parts')

    @pyd.model_validator(mode='before')
    @classmethod
    def convert_parts(cls, obj: Any) -> Any:
        if isinstance(obj, dict) and isinstance(obj.get('parts'), list):
            if len(obj['parts']) == 1:
                obj['parts'] = obj['parts'][0]
            else:
                obj['parts'] = ''.join(obj['parts'])
        return obj


class CodeContent(Model):
    content_type: Lit['code']
    language: Lit['unknown']
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
    tether_id: int | None = None


class BrowserQuoteContent(Model):
    content_type: Lit['tether_quote']
    url: str
    domain: str
    text: str
    title: str
    tether_id: None = None

class SonicWebpageContent(Model):
    content_type: Lit['sonic_webpage']
    url: str
    domain: str
    title: str
    text: str
    snippet: str | None = None
    pub_date: float | None = None
    crawl_date: float | None = None
    pub_timestamp: float | None = None
    ref_id: str | None = None

class MultimodalTextContent(Model):
    content_type: Lit['multimodal_text']
    parts: list[ContentPart | str] | None = None

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
    metadata: ImageMetadata | None

type ContentPart = Annotated[
    TextContentPart | ImageContentPart,
    pyd.Discriminator('content_type'),
]

class ImageMetadata(Model):
    dalle: Dalle
    gizmo: None = None
    generation: Generation | None = None
    container_pixel_height: int | None = None
    container_pixel_width: int | None = None
    emu_omit_glimpse_image: None = None
    emu_patches_override: None = None
    sanitized: bool
    asset_pointer_link: None = None
    watermarked_asset_pointer: None = None
    lpe_keep_patch_ijhw: None = None
    


class Generation(Model):
    gen_id: str | None = None
    gen_size: Lit['xlimage', 'image']
    seed: int | None = None
    parent_gen_id: None = None
    height: int | None = None
    width: int | None = None
    transparent_background: bool | None = None
    serialization_title: str | None = None


class Dalle(Model):
    gen_id: str | None
    prompt: str
    seed: int | None
    parent_gen_id: str | None
    edit_op: str | None
    serialization_title: str


class ComputerOutputContent(Model):
    content_type: Lit['computer_output']
    computer_id: str
    screenshot: ImageContentPart | None = None
    tether_id: int | None = None
    state: ComputerOutputState | None = None
    text: str | None = None
    is_ephemeral: bool | None = None

class ComputerOutputState(Model):
    type: Lit['computer_initialize_state']
    id: str
    os_type: Lit['computer']
    os_name: str
    os_version: str
    target_type: Lit['host']
    target_name: str | None = None
    installed_software: list[str]


type Content = Annotated[
    TextContent
    | ErrorContent
    | CodeContent
    | ExecutionOutputContent
    | BrowserDisplayContent
    | BrowserQuoteContent
    | MultimodalTextContent
    | ComputerOutputContent
    | SonicWebpageContent,
    pyd.Discriminator('content_type'),
]


class Metadata(Model):
    message_type: Lit['next'] | None = None
    model_slug: ModelName | None = None
    timestamp_: Lit['absolute']
    default_model_slug: ModelName | None = None
    requested_model_slug: ModelName | None = None
    parent_id: str | None = None
    request_id: str | None = None
    is_complete: bool | None = None
    aggregate_result: dict | None = None
    cite_metadata: dict | None = pyd.Field(None, alias='_cite_metadata')
    status: Lit['finished', 'failed', 'running'] | None = None
    is_visually_hidden_from_conversation: bool | None = None
    pad: str | None = None
    jit_plugin_data: dict | None = None
    gizmo_id: str | None = None
    voice_mode_message: bool | None = None
    reasoning_status: Lit['is_reasoning'] | None = None
    reasoning_group_id: str | None = None
    needs_startup: bool | None = None
    debug_sonic_thread_id: str | None = None
    initial_text: str | None = None
    finished_duration_sec: int | None = None
    finished_text: str | None = None
    cloud_doc_urls: list[None] | None = None
    command: Command | None = None
    args: str | list[Any] | None = None
    kwargs: MetadataKwargs | None = None
    finish_details: FinishDetails | None = None
    invoked_plugin: InvokedPlugin | None = None
    search_result_groups: list[SearchResultGroup] | None = None
    ada_visualizations: list[Visualization] | None = None
    canvas: Canvas | None = None
    search_turns_count: int | None = None
    search_source: Lit['composer_auto', 'composer_search'] | None = None
    client_reported_search_source: Lit['composer_auto', 'conversation_composer_web_icon', 'conversation_composer_previous_web_mode'] | None = None
    async_task_title: str | None = None
    async_task_prompt: str | None = None
    async_task_type: Lit['research'] | None = None
    b1de6e2_s: bool | None = None
    async_task_id: str | None = None
    async_task_conversation_id: str | None = None
    async_task_created_at: str | None = None
    deep_research_version: Lit['full'] | None = None
    permissions: list[Permissions] | None = None
    async_task_status_messages: AsyncTaskStatusMessage | None = None
    source: Lit['computer'] | None = None
    n7jupd_message: bool | None = None
    n7jupd_title: str | None = None
    n7jupd_titles: list[str] | None = None
    n7jupd_url: str | None = None
    n7jupd_urls: list[str] | None = None
    n7jupd_subtool: SubTool | None = None
    clicked_from_url: None = None
    clicked_from_title: None = None
    connector_source: str | None = None
    display_url: str | None = None
    display_title: str | None = None
    content_references: list[Any] | None = None
    citations: list[None] | None = None
    image_gen_title: str | None = None
    is_error: bool | None = None



class SubTool(Model):
    generic_api_func: str | None = None
    subtool: str | None = None
    used_internet: bool = False
    changed_url: bool = False
    result_of_subtool: str | None = None

class AsyncTaskStatusMessage(Model):
    initial: str | None = None
    completed_with_time: str | None = None
    completed_no_time: str | None = None
    completed: str | None = None
    error: str | None = None
    cancelled: str | None = None


class Permissions(Model):
    type: Lit['notification']
    status: Lit['requested'] 
    notification_channel_id: Lit['deep_research', 'chatgpt_agent'] | None = None
    notification_channel_name: Lit['Research', 'Agent'] | None = None
    notification_priority: int


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
    chart_type: Lit['bar', 'scatter','']
    fallback_to_image: bool


type Visualization = Annotated[
    VisualizationTable | VisualizationChart,
    pyd.Discriminator('type'),
]


class Canvas(Model):
    textdoc_id: str | None = None
    textdoc_type: Lit['document', 'code/python', 'code/sql', 'code/javascript', 'code/html'] | None = None
    version: int | None = None
    title: str | None = None
    create_source: Lit['model', 'system_hint_canvas'] | None = None
    from_version: int | None = None
    has_user_edit: bool | None = None
    textdoc_content_length: int | None = None
    user_message_type: Lit['ask_chatgpt','accelerator'] | None = None
    selection_metadata: SelectionMetadata | None = None
    accelerator_metadata: AcceleratorMetadata | None = None


class AcceleratorMetadata(Model):
    action: Lit['comment']
    id: str
    prompt: str | None = None



class SelectionMetadata(Model):
    selection_type: Lit['selection']
    selection_position_range: SelectionPositionRange | None = None

class SelectionPositionRange(Model):
    start: int
    end: int



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
    'clarify_with_text',
    'start_research_task',
    'update_textdoc',
    'spinner',
    'msearch',
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
