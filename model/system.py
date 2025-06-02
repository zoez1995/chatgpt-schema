from __future__ import annotations
import pydantic as pyd
from typing import Literal as Lit, Any
from .config import Model, ModelName


class SystemMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'system'
    """

    id: str
    parent: str
    role: Lit['system']
    name: None
    author_metadata: None
    create_time: float | None
    update_time: None
    status: Lit['finished_successfully']
    end_turn: bool | None
    weight: float
    recipient: Lit['all']
    channel: None
    content: Content
    metadata: Metadata
    children: list[str]


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
