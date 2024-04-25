from __future__ import annotations
from typing import Literal
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
    mapping: dict[str, RootNode | MessageNode]
    moderation_results: list[None]
    current_node: str
    plugin_ids: list[str] | None
    conversation_id: str
    conversation_template_id: str | None
    gizmo_id: str | None
    is_archived: Literal[False]
    safe_urls: list[str]
    default_model_slug: str | None
    id: str


class RootNode(Model):
    id: str
    message: None
    parent: None
    children: list[str]


class MessageNode(Model):
    id: str
    message: Message
    parent: str
    children: list[str]


Message = UserMessage | AssistantMessage | SystemMessage | ToolMessage


Conversation.model_rebuild()
