from __future__ import annotations
from typing import Literal as Lit, Annotated, Any
import pydantic as pyd
from .user import UserMessage
from .assistant import AssistantMessage
from .system import SystemMessage
from .tool import ToolMessage
from .config import Model


class Conversation(Model):
    """
    An element in the `conversations.json` array of your ChatGPT export.
    """

    title: str
    create_time: float
    update_time: float
    mapping: dict[str, Node]
    moderation_results: list[None]
    current_node: str
    plugin_ids: list[str] | None
    conversation_id: str
    conversation_template_id: str | None
    gizmo_id: str | None
    gizmo_type: Lit['gpt'] | None
    is_archived: Lit[False]
    is_starred: None
    safe_urls: list[str]
    blocked_urls: list[None]
    default_model_slug: str | None
    conversation_origin: None
    voice: None
    async_status: int | None
    disabled_tool_ids: list[Lit['canmore']]
    is_do_not_remember: Lit[False] | None
    memory_scope: Lit['global_enabled']
    id: str

    @pyd.model_validator(mode='before')
    @classmethod
    def nullify_empty_dicts(cls, obj: Any) -> Any:
        """
        Recursively nullify empty dictionaries in the model.
        This is useful for cleaning up the model before serialization.
        """
        return nullify_empty_dicts_rec(obj)


def nullify_empty_dicts_rec(obj: Any) -> Any:
    if obj == {}:
        return None
    if isinstance(obj, dict):
        return {k: nullify_empty_dicts_rec(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [nullify_empty_dicts_rec(item) for item in obj]
    return obj


class Node(Model):
    id: str
    parent: str | None
    message: Message | None
    children: list[str]

    @pyd.field_validator('message', mode='before')
    @classmethod
    def set_message_role(cls, value: Any) -> Any:
        if isinstance(value, dict):
            value['role'] = value['author']['role']
        return value


Message = Annotated[
    UserMessage | AssistantMessage | SystemMessage | ToolMessage,
    pyd.Discriminator('role'),
]

Conversation.model_rebuild()
