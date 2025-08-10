"""
Defines the structure of an assistant message.
"""

from __future__ import annotations
from typing import Any, Literal as Lit, Annotated
import pydantic as pyd
from .config import Model, DefaultToolName, ModelName, PluginName
from . import contentref
from .tool import Canvas

class AssistantMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'assistant'
    """

    id: str
    parent: str
    role: Lit['assistant']
    name: None
    author_metadata: AuthorMetadata | None
    create_time: float
    update_time: None
    status: Status
    end_turn: bool | None
    weight: float
    recipient: Lit['all'] | DefaultToolName | PluginName
    channel: Lit['final', 'commentary'] | None = None
    content: Content
    metadata: Metadata
    children: list[str]


type Status = Lit['finished_successfully', 'in_progress', 'finished_partial_completion']


type Content = Annotated[
    TextContent | CodeContent | ThoughtsContent | ReasoningRecapContent | MultiModalTextContent,
    pyd.Discriminator('content_type'),
]


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
    language: Lit['unknown', 'json']
    text: str
    response_format_name: None = None


class ThoughtsContent(Model):
    content_type: Lit['thoughts']
    thoughts: list[Thought]
    source_analysis_msg_id: str


class ReasoningRecapContent(Model):
    content_type: Lit['reasoning_recap']
    text: str = pyd.Field(alias='content')

class MultiModalTextContent(Model):
    content_type: Lit['multimodal_text']
    parts: list[AudioContent]

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
    
type AudioContent = Annotated[
    AudioTranscription | AudioAssetPointer | RealTimeAudioContent,
    pyd.Discriminator('content_type'),
]

class AudioTranscription(Model):
    content_type: Lit['audio_transcription']
    text: str
    direction: Lit['out'] | None = None
    decoding_id: None = None


class AudioAssetPointer(Model):
    expiry_datetime: str | None = None
    content_type: Lit['audio_asset_pointer']
    asset_pointer: str
    size_bytes: int
    format: Lit['wav']
    metadata: AudioMetadata | None = None

class AudioMetadata(Model):
    start_timestamp: float | None = None
    end_timestamp: float | None = None
    pretokenized_vq: None = None
    interruptions: None = None
    original_audio_source: None = None
    transcription: str | None = None
    word_transcription: list[None] | None = None
    start: float | None = 0.0
    end: float | None = 0.0

class RealTimeAudioContent(Model):
    expiry_datetime: str | None = None
    content_type: Lit['real_time_user_audio_video_asset_pointer']
    frames_asset_pointers: list[str] | None = None
    video_container_asset_pointer: str | None = None
    audio_asset_pointer: AudioAssetPointer | None = None
    audio_start_timestamp: float | None = None

class Thought(Model):
    summary: str
    text: str = pyd.Field(alias='content')


class AuthorMetadata(Model):
    real_author: Lit['tool:web']
    sonicberry_model_id: Lit['current_sonicberry_paid','alpha.sonicberry_2s_p'] | None = None
    source: Lit['sonic_tool'] | None = None


class Metadata(Model):
    model_slug: ModelName | None = None
    message_type: Lit['next'] | None = None
    timestamp_: Lit['absolute']
    message_locale: str | None = None
    default_model_slug: ModelName | None = None
    pad: str | None = None
    parent_id: str | None = None
    request_id: str | None = None
    gizmo_id: str | None = None
    voice_mode_message: bool | None = None
    requested_model_slug: ModelName | None = None
    reasoning_status: ReasoningStatus | None = None
    finished_duration_sec: int | None = None
    search_source: SearchSource | None = None
    client_reported_search_source: SearchSource | None = None
    search_display_string: str | None = None
    searched_display_string: str | None = None
    is_complete: Lit[True] | None = None
    is_visually_hidden_from_conversation: Lit[True] | None = None
    filter_out_for_training: Lit[True] | None = None
    debug_sonic_thread_id: str | None = None
    augmented_paragen_prompt_label: str | None = None
    safe_urls: list[str] | None = None
    finish_details: FinishDetails | None = None
    citations: list[Citation] | None = None
    content_references: list[contentref.ContentReference] | None = None
    search_queries: list[SearchQuery] | None = None
    search_result_groups: list[SearchResultGroup] | None = None
    sonic_classification_result: SonicClassificationResult | None = None
    image_results: list[contentref.Image] | None = None
    search_turns_count: int | None = None
    is_async_task_result_message: bool | None = None
    b1de6e2_rm: bool | None = None
    async_task_id: str | None = None
    async_task_title: str | None = None
    is_loading_message: bool | None = None
    n7jupd_message: bool | None = None
    reasoning_group_id: str | None = None
    stop_reason: None = None
    n7jupd_subtool: SubTool | None = None
    n7jupd_schedulable: bool | None = None
    n7jupd_summary: str | None = None
    n7jupd_crefs: list[Any] | None = None
    n7jupd_crefs_by_file: dict[str, Any] | None = None
    content_references_by_file: dict[str, list[contentref.ContentReference]] | None = None
    is_visually_hidden_reasoning_group: bool | None = None
    canvas: Canvas | None = None
    safety_plugin_status_code: int | None = None
    model_switcher_deny: list[ModelSwitcherDeny] | None = None
    message_source: None = None


class ModelSwitcherDeny(Model):
    slug: ModelName | Lit['auto']
    context: Lit['regenerate','conversation']
    reason: Lit['unsupported_canvas']
    description: str


class SubTool(Model):
    generic_api_func: str | None = None
    subtool: str | None = None
    used_internet: bool = False
    changed_url: bool = False
    result_of_subtool: str | None = None



type ReasoningStatus = Lit['is_reasoning', 'reasoning_ended']


type SearchSource = Lit[
    'composer_auto',
    'composer_search',
    'composer_auto',
    'conversation_composer_web_icon',
    'conversation_composer_previous_web_mode',
    'url_no_search_hint',
]


class SonicClassificationResult(Model):
    latency_ms: float | None
    search_prob: float | None
    force_search_threshold: float | None = None
    classifier_config_name: ClassifierConfigName | None = None
    complex_search_prob: float | None = None
    search_complexity: Lit['simple'] | None = None



type ClassifierConfigName = Lit['sonic_force_pg_switcher_renderer_config','sonic_classifier_ev3']


class SearchQuery(Model):
    type: Lit['search']
    q: str


class SearchResultGroup(Model):
    type: Lit['search_result_group']
    domain: str
    entries: list[SearchResultGroupEntry]


class SearchResultGroupEntry(Model):
    type: Lit['search_result']
    url: str
    title: str
    snippet: str
    ref_id: contentref.Ref
    pub_date: float | None
    attribution: str | None = None
    attributions: None = None
    attributions_debug: None = None
    content_type: None = None


class FinishDetailsMaxTokens(Model):
    type: Lit['max_tokens']


class FinishDetailsStop(Model):
    type: Lit['stop']
    stop_tokens: list[int] | None = None
    stop: str | None = None


class FinishDetailsInterrupted(Model):
    type: Lit['interrupted']
    reason: Lit['client_stopped'] | None = None


FinishDetails = Annotated[
    FinishDetailsStop | FinishDetailsInterrupted | FinishDetailsMaxTokens,
    pyd.Discriminator('type'),
]


class Citation(Model):
    start_ix: int
    end_ix: int
    citation_format_type: Lit['tether_og', 'tether_v4'] | None = None
    invalid_reason: str | None = None
    metadata: CitationMetadata | None = None


class CitationMetadataWebpage(Model):
    type: Lit['webpage']
    title: str = None
    url: str
    text: str
    pub_date: str | None = None
    og_tags: None = None
    extra: CitationMetadataExtra | None
    


class CitationMetadataOther(Model):
    type: Lit['file']
    title: str | None = None
    url: str | None = None
    text: str | None = None
    pub_date: None = None
    name: str | None = None
    id: str | None = None
    source: str | None = None
    extra: dict[str, Any] | None = None

class CitationMetadataImage(Model):
    type: Lit['image_inline']
    asset_pointer_links: list[str]
    clicked_from_url: str | None = None
    clicked_from_title: str | None = None

type CitationMetadata = Annotated [
    CitationMetadataWebpage | CitationMetadataOther | CitationMetadataImage,
    pyd.Discriminator('type'),
]


class CitationMetadataExtra(Model):
    evidence_text: str = None
    cited_message_idx: int
    search_result_idx: int | None = None
    cloud_doc_url: None = None
    cited_message_id: str | None = None
    start_line_num: int | None = None
    end_line_num: int | None = None
    connector_source: str | None = None


# Keep at end of file
AssistantMessage.model_rebuild()
