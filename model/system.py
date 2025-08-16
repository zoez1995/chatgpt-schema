from __future__ import annotations
import pydantic as pyd
from typing import Literal as Lit, Any
from .config import Model, ModelName
from .tool import Canvas

class SystemMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'system'
    """

    id: str
    parent: str
    role: Lit['system']
    name: None
    author_metadata: SystemInitiated | None
    create_time: float | None
    update_time: None
    status: Lit['finished_successfully']
    end_turn: bool | None
    weight: float
    recipient: Lit['all', 'assistant']
    channel: None = None
    content: Content
    metadata: Metadata
    children: list[str]

class SystemInitiated(Model):
    is_system_initiated_conversation: Lit[True]

class Content(Model):
    content_type: Lit['text']
    text: str = pyd.Field(alias='parts')

    @pyd.model_validator(mode='before')
    @classmethod
    def convert_parts(cls, obj: Any) -> Any:
        if isinstance(obj, dict) and isinstance(obj.get('parts'), list):
            assert len(obj['parts']) == 1
            obj['parts'] = obj['parts'][0]
        return obj


class Metadata(Model):
    is_visually_hidden_from_conversation: Lit[True]
    is_complete: Lit[True] | None = None
    is_user_system_message: Lit[True] | None = None
    user_context_message_data: UserContextMessageData | None = None
    rebase_system_message: Lit[True] | None = None
    rebase_developer_message: Lit[True] | None = None
    message_type: Lit['next', 'variant'] | None = None
    message_source: Lit['instant-query'] | None = None
    model_slug: ModelName | None = None
    requested_model_slug: ModelName | None = None
    default_model_slug: ModelName | None = None
    parent_id: str | None = None
    request_id: str | None = None
    timestamp_: Lit['absolute'] | None = None
    attachments: list[Attachment] | None = None
    voice_mode_message: bool | None = None
    finish_details: FinishDetails | None = None
    gizmo_id: str | None = None
    pad: str | None = None
    system_hints: list[str] | None = None
    exclusive_key: str | None = None
    canvas: Canvas | None = None
    paragen_variants_info: ParagenVariants | None = None
    citations: list[None] | None = None
    content_references: list[None] | None = None
    command: Lit['prompt'] | None = None
    is_contextual_answers_system_message: bool | None = None
    contextual_answers_message_type: Lit['sources_and_filters_prompt', 'identity_prompt'] | None = None


class ParagenVariants(Model):
    type: Lit['num_variants_in_stream']
    num_variants_in_stream: int
    display_treatment: Lit['skippable']
    conversation_id: str | None = None



class FinishDetails(Model):
    type: Lit['stop']
    stop_tokens: list[float]


class Attachment(Model):
    id: str
    name: str
    mimeType: str
    fileSizeTokens: None = None


class UserContextMessageData(Model):
    about_user_message: str | None = None
    about_model_message: str | None = None


# Keep at end of file
SystemMessage.model_rebuild()
