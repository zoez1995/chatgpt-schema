"""
Defines the structure of an assistant message.
"""

from __future__ import annotations
from typing import Literal as Lit, Annotated
import pydantic as pyd
from .config import Model, DefaultToolName, PluginName
from . import contentref


class AssistantMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'assistant'
    """

    id: str
    role: Lit['assistant']
    author: Author
    create_time: float
    update_time: None
    content: Content
    status: Status
    end_turn: bool | None
    weight: float
    metadata: Metadata
    recipient: Lit['all'] | DefaultToolName | PluginName
    channel: Lit['final', 'commentary'] | None


type Status = Lit['finished_successfully', 'in_progress', 'finished_partial_completion']


type Content = Annotated[
    TextContent | CodeContent | ThoughtsContent | ReasoningRecapContent,
    pyd.Discriminator('content_type'),
]


class TextContent(Model):
    content_type: Lit['text']
    parts: list[str]


class CodeContent(Model):
    content_type: Lit['code']
    language: str
    text: str
    response_format_name: None


class ThoughtsContent(Model):
    content_type: Lit['thoughts']
    thoughts: list[Thought]
    source_analysis_msg_id: str


class ReasoningRecapContent(Model):
    content_type: Lit['reasoning_recap']
    content: str


class Thought(Model):
    summary: str
    content: str


class Author(Model):
    role: Lit['assistant']
    name: None
    metadata: AuthorMetadata | None


class AuthorMetadata(Model):
    real_author: Lit['tool:web']


class Metadata(Model):
    model_slug: str
    message_type: None
    timestamp_: Lit['absolute']
    message_locale: str | None = None
    default_model_slug: str | None = None
    pad: str | None = None
    parent_id: str | None = None
    request_id: str | None = None
    gizmo_id: str | None = None
    voice_mode_message: bool | None = None
    requested_model_slug: str | None = None
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


type ReasoningStatus = Lit['is_reasoning', 'reasoning_ended']


type SearchSource = Lit[
    'composer_auto',
    'composer_search',
    'composer_auto',
    'conversation_composer_web_icon',
]


class SonicClassificationResult(Model):
    latency_ms: float | None
    search_prob: float | None
    force_search_threshold: float | None = None
    classifier_config_name: ClassifierConfigName | None = None


type ClassifierConfigName = Lit['sonic_force_pg_switcher_renderer_config',]


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
    citation_format_type: Lit['tether_og'] | None = None
    invalid_reason: str | None = None
    metadata: CitationMetadata | None = None


class CitationMetadataWebpage(Model):
    type: Lit['webpage']
    title: str
    url: str
    text: str
    pub_date: str | None
    og_tags: None = None
    extra: CitationMetadataExtra | None


class CitationMetadataOther(Model):
    title: str
    url: str
    text: str
    pub_date: None


type CitationMetadata = CitationMetadataWebpage | CitationMetadataOther


class CitationMetadataExtra(Model):
    evidence_text: str
    cited_message_idx: int
    search_result_idx: int | None = None
    cloud_doc_url: None = None


# Keep at end of file
AssistantMessage.model_rebuild()
