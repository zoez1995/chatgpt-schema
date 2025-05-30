from __future__ import annotations
import pydantic as pyd
from typing import Literal as Lit, Annotated
from .config import Model


class UserMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'user'
    """

    id: str
    role: Lit['user']
    author: Author
    create_time: float
    update_time: None
    content: Content
    status: Lit['finished_successfully']
    end_turn: None
    weight: float
    metadata: Metadata
    recipient: Lit['all']
    channel: None


class Author(Model):
    role: Lit['user']
    name: None
    metadata: None


type Content = Annotated[
    TextContent | MultimodalTextContent | ImageContent,
    pyd.Discriminator('content_type'),
]


class TextContent(Model):
    content_type: Lit['text']
    parts: list[str]


class MultimodalTextContent(Model):
    content_type: Lit['multimodal_text']
    parts: list[str | ImageContent]


class ImageContent(Model):
    content_type: Lit['image_asset_pointer']
    asset_pointer: str
    size_bytes: int
    width: int
    height: int
    fovea: None
    metadata: ImageMetadata | None


class ImageMetadata(Model):
    dalle: None
    gizmo: None
    generation: None
    container_pixel_height: None
    container_pixel_width: None
    emu_omit_glimpse_image: None
    emu_patches_override: None
    sanitized: Lit[True]
    asset_pointer_link: None
    watermarked_asset_pointer: None


class Metadata(Model):
    request_id: str | None = None
    timestamp_: Lit['absolute']
    message_type: None
    attachments: list[Attachment] | None = None
    targeted_reply: str | None = None
    voice_mode_message: Lit[True] | None = None
    gizmo_id: str | None = None
    message_source: None = None
    selected_sources: list[Lit['web']] | None = None
    selected_github_repos: list[None] | None = None
    serialization_metadata: SerializationMetadata | None = None
    paragen_variants_info: ParagenVariantsInfo | None = None
    paragen_variant_choice: str | None = None
    caterpillar_selected_sources: list[Lit['web']] | None = None
    system_hints: list[Lit['search']] | None = None


class Attachment(Model):
    id: str
    name: str
    size: int
    url: str | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    file_token_size: int | None = None


class SerializationMetadata(Model):
    custom_symbol_offsets: list[None]


class ParagenVariantsInfo(Model):
    type: Lit['num_variants_in_stream']
    num_variants_in_stream: int
    display_treatment: Lit['skippable']
    conversation_id: str


# Keep at end of file
UserMessage.model_rebuild()
