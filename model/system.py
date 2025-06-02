from __future__ import annotations
from typing import Literal as Lit
from .config import Model, ModelName


class SystemMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'system'
    """

    id: str
    role: Lit['system']
    author: Author
    create_time: float | None
    update_time: None
    content: Content
    status: Lit['finished_successfully']
    end_turn: bool | None
    weight: float
    metadata: Metadata
    recipient: Lit['all']
    channel: None


class Author(Model):
    role: Lit['system']
    name: None
    metadata: None


class Content(Model):
    content_type: Lit['text']
    parts: list[str]


class Metadata(Model):
    is_visually_hidden_from_conversation: Lit[True]
    is_complete: Lit[True] | None = None
    is_user_system_message: Lit[True] | None = None
    user_context_message_data: UserContextMessageData | None = None
    rebase_system_message: Lit[True] | None = None
    rebase_developer_message: Lit[True] | None = None
    message_type: None = None
    message_source: None = None
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
    pad: Lit['AAAAAAAAAAAAAAAAAAA'] | None = None


class FinishDetails(Model):
    type: Lit['stop']
    stop_tokens: list[float]


class Attachment(Model):
    id: str
    name: str
    mimeType: str


class UserContextMessageData(Model):
    about_user_message: str | None = None
    about_model_message: str | None = None


# Keep at end of file
SystemMessage.model_rebuild()
