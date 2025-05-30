"""
Content references in the metadata of assistant messages.
"""

from __future__ import annotations
from typing import Literal as Lit
from .config import Model


class ContentReference(Model):
    type: Lit[
        'webpage',
        'webpage_extended',
        'nav_list',
        'navigation',
        'grouped_webpages',
        'sources_footnote',
        'hidden',
        'image_v2',
        'attribution',
        'grouped_webpages_model_predicted_fallback',
        'tldr',
    ]
    matched_text: str
    start_idx: int
    end_idx: int
    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    attribution: str | None = None
    pub_date: float | None = None
    status: Lit['done'] | None = None
    safe_urls: list[str] | None = None
    refs: list[NamedRef] | list[Ref] | None = None
    alt: str | None = None
    prompt_text: str | None = None
    items: list[Item] | None = None
    error: None = None
    style: str | None = None
    has_images: bool | None = None
    sources: list[Source] | None = None
    invalid: bool | None = None
    attributions: None = None
    attributions_debug: None = None
    attributable_index: str | None = None
    images: list[Image] | None = None
    domains: list[Domain] | None = None
    display_title: str | None = None
    page_title: str | None = None
    leaf_description: str | None = None
    used_as_navigation: Lit[True] | None = None
    breadcrumbs: list[str] | None = None
    icon_type: None = None


type NamedRef = Lit[
    'malformed',
    'hidden',
    'optimistic_image',
]


class Domain(Model):
    title: str
    subtitle: str
    domain: str
    url: str
    sub_domains: list[None]
    attribution: str


class Source(Model):
    title: str
    url: str
    attribution: str


class Ref(Model):
    ref_type: RefType
    turn_index: int
    ref_index: int


type RefType = Lit['search', 'image', 'view', 'news', 'fetch']


class Item(Model):
    title: str
    url: str
    thumbnail_url: str | None = None
    pub_date: float | None
    snippet: str | None = None
    hue: None = None
    attributions: None = None
    attribution: str | None = None
    attribution_segments: list[str] | None = None
    supporting_websites: list[SupportingWebsite] | None = None
    refs: list[Ref] | None = None


class SupportingWebsite(Model):
    title: str
    url: str
    pub_date: float | None
    attribution: str
    snippet: str | None = None


class Image(Model):
    url: str
    content_url: str
    thumbnail_url: str
    title: str
    content_size: Size
    thumbnail_size: Size
    thumbnail_crop_info: None = None
    attribution: str


class Size(Model):
    width: int
    height: int
