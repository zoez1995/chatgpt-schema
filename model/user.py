from __future__ import annotations
import pydantic as pyd
from typing import Any, Literal as Lit, Annotated
from .config import Model
from .tool import Canvas


class UserMessage(Model):
    """
    A message at `Conversation.mapping[<id>].message` where author.role == 'user'
    """

    id: str
    parent: str
    role: Lit['user']
    name: None
    author_metadata: None
    create_time: float | None
    update_time: None
    status: Lit['finished_successfully']
    end_turn: None
    weight: float
    recipient: Lit['all']
    channel: None = None
    content: Content
    metadata: Metadata
    children: list[str]


type Content = Annotated[
    TextContent | MultimodalTextContent | ImageContent | UserEditableContent,
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


class MultimodalTextContent(Model):
    content_type: Lit['multimodal_text']
    parts: list[TextContentPart | ImageContent | AudioContent]

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

class UserEditableContent(Model):
    content_type: Lit['user_editable_context']
    user_profile: str 
    user_instructions: str

class TextContentPart(Model):
    content_type: Lit['text']
    text: str | None = None

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
    lpe_keep_patch_ijhw: None = None

type AudioContent = Annotated[
    AudioTranscription | AudioAssetPointer | RealTimeAudioContent,
    pyd.Discriminator('content_type'),
]
class AudioTranscription(Model):
    content_type: Lit['audio_transcription']
    text: str
    direction: Lit['in'] | None = None
    decoding_id: None = None

class RealTimeAudioContent(Model):
    expiry_datetime: str | None = None
    content_type: Lit['real_time_user_audio_video_asset_pointer']
    frames_asset_pointers: list[str] | None = None
    video_container_asset_pointer: str | VideoContainerAssetPointer | None = None
    audio_asset_pointer: AudioAssetPointer | None = None
    audio_start_timestamp: float | None = None


class VideoContainerAssetPointer(Model):
    content_type: Lit['video_container_asset_pointer']
    asset_pointer: str
    size_bytes: int
    format: Lit['mp4']
    frame_attributes: list[VideoFrameAttribute] | None = None

class VideoFrameAttribute(Model):
    frame_index: int
    timestamp: float
    metadata:  dict[str, Any] | None = None


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


class Metadata(Model):
    request_id: str | None = None
    timestamp_: Lit['absolute'] = None
    message_type: Lit['next'] | None = None
    attachments: list[Attachment] | None = None
    targeted_reply: str | None = None
    voice_mode_message: Lit[True] | None = None
    gizmo_id: str | None = None
    message_source: Lit['instant-query'] | None = None
    selected_sources: list[SelectedSource] | None = None
    selected_github_repos: list[None] | None = None
    serialization_metadata: SerializationMetadata | None = None
    paragen_variants_info: ParagenVariantsInfo | None = None
    paragen_variant_choice: str | None = None
    caterpillar_selected_sources: list[SelectedSource] | None = None
    system_hints: list[Lit['search','research','agent','canvas', 'moonshine']] | None = None
    is_visually_hidden_from_conversation: bool | None = None
    user_context_message_data: UserContextMessageData | None = None
    is_user_system_message: bool | None = None
    dictation: bool | None = None
    dictation_edited: bool | None = None
    selected_mcp_sources: list[None] | None = None
    real_time_audio_has_video: bool | None = None
    targeted_reply_label: str | None = None
    canvas: Canvas | None = None
    dalle: dict[str, Any] | None = None
    




type SelectedSource = Lit[
    'web',
    'merge_file_storage_sync_connector',
    'github_sync_connector',
    'gdrive_sync_connector',
    'slack_sync_connector',
    'notion_sync_connector',
]

class UserContextMessageData(Model):
    about_user_message: str

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
    custom_symbol_offsets: list[None] | list[CustomSymbolOffsets]


class CustomSymbolOffsets(Model):
    symbol: str
    startIndex: int
    endIndex: int


class ParagenVariantsInfo(Model):
    type: Lit['num_variants_in_stream']
    num_variants_in_stream: int
    display_treatment: Lit['skippable']
    conversation_id: str


# Keep at end of file
UserMessage.model_rebuild()
