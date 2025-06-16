from __future__ import annotations
from typing import Literal as Lit, Annotated, Any
import pydantic as pyd
from .user import UserMessage
from .assistant import AssistantMessage
from .system import SystemMessage
from .tool import ToolMessage
from .config import Model, ModelName


class Conversation(Model):
    """
    An element in the `conversations.json` array of your ChatGPT export.
    """

    id: str
    title: str
    create_time: float
    update_time: float
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
    default_model_slug: ModelName | None
    conversation_origin: None
    voice: None
    async_status: int | None
    disabled_tool_ids: list[Lit['canmore']]
    is_do_not_remember: Lit[False] | None
    memory_scope: Lit['global_enabled']
    mapping: dict[str, Node]

    @pyd.model_validator(mode='before')
    @classmethod
    def nullify_empty_dicts(cls, obj: Any) -> Any:
        """
        Recursively nullify empty dictionaries in the model.
        This is useful for cleaning up the model before serialization.
        """
        return nullify_empty_dicts_rec(obj)

    @pyd.field_validator('mapping', mode='before')
    @classmethod
    def flatten_message_nodes(cls, mapping: dict) -> Any:
        assert mapping
        first_node = next(iter(mapping.values()))

        if not 'message' in first_node:
            # Already flattened
            return mapping

        def flatten_message_node(node: dict) -> dict:
            msg = node.pop('message')
            if msg is None:
                node['role'] = 'root'
                return node

            msg['id'] = node['id']
            msg['parent'] = node['parent']
            msg['children'] = node['children']

            # Flatten author
            assert 'role' not in msg
            assert 'name' not in msg
            assert 'author_metadata' not in msg
            author = msg.pop('author')
            assert author
            msg['role'] = author['role']
            msg['name'] = author['name']
            msg['author_metadata'] = author['metadata']
            return msg

        return {
            k: flatten_message_node(v) for k, v in mapping.items()
        }

    def get_root_node(self) -> RootNode:
        for node in self.mapping.values():
            if node.parent is None and node.role == 'root':
                return node
        raise ValueError("No root node found in the conversation mapping.")


def nullify_empty_dicts_rec(obj: Any) -> Any:
    if obj == {}:
        return None
    if isinstance(obj, dict):
        return {k: nullify_empty_dicts_rec(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [nullify_empty_dicts_rec(item) for item in obj]
    return obj


class RootNode(Model):
    id: str
    parent: None
    role: Lit['root']
    children: list[str]


type Message = Annotated[
    UserMessage | AssistantMessage | SystemMessage | ToolMessage,
    pyd.Discriminator('role'),
]

type Node = Annotated[
    RootNode | Message,
    pyd.Discriminator('role'),
]

Conversation.model_rebuild()
