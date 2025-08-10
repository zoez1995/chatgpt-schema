"""
Content references in the metadata of assistant messages.
"""

from __future__ import annotations
from typing import Literal as Lit
from typing import Any
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
        'image_inline',
        'video',
        'products',
        'product_entity',
        'businesses_map',
        'file',     
    ]
    matched_text: str
    start_idx: int
    end_idx: int
    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    attribution: str | None = None
    pub_date: float | None = None
    status: Lit['done', 'loading', 'error'] | None = None
    safe_urls: list[str] | None = None
    refs: list[NamedRef] | list[Ref] | None = None
    alt: str | None = None
    prompt_text: str | None = None
    items: list[Item] | None = None
    fallback_items: list[Item] | None = None
    error: str | None = None
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
    clicked_from_title: str | None = None
    clicked_from_url: str | None = None
    asset_pointer_links: list[str] | None = None
    user_time_zone: str | None = None
    thumbnail_url: str | None = None
    video_site: str | None = None
    video_id: str | None = None
    prompt_obj: None = None
    product: Product | None = None
    products: list[Product] | None = None
    target_product_count: int | None = None
    cite_map: dict[str, Cite] | None = None
    navigation_fallback: None = None
    businesses: list[Any] | None = None
    business_fallbacks: list[Any] | None = None
    render_fallbacks: bool | None = None
    fff_metadata: None = None
    input_pointer: dict[str, Any] | None = None
    cloud_doc_url: None = None
    id: str | None = None
    name: str | None = None
    source: str | None = None


                                
class Cite(Model):
    cite: str
    title: str | None = None
    url: str | None = None
    pub_date: float | None = None
    snippet: str | None = None
    attribution: str | None = None

type NamedRef = Lit[
    'malformed',
    'hidden',
    'optimistic_image',
    'optimistic_map',

]


class Product(Model):
    query: str | None = None
    provider: str | None = None
    id: str | None = None
    title: str | None = None
    providers: list[str] | None = None
    metadata_sources: list[str] | None = None
    product_lookup_data: dict[str, Any] | None = None
    url: str | None = None
    merchants: str | None = None
    price: str | None = None
    description: str | None = None
    featured_tag: str | None = None
    image_urls: list[str] | None = None
    num_reviews: int | None = None
    rating: float | None = None
    cite: str | None = None
    rating_grouped_citation: str | None = None
    offers: list[dict[str, Any]] | None = None

class Domain(Model):
    title: str
    subtitle: str
    domain: str
    url: str
    sub_domains: list[SubDomains]
    attribution: str

class SubDomains(Model):
    url: str | None = None
    title: str | None = None

class Source(Model):
    title: str
    url: str
    attribution: str


class Ref(Model):
    ref_type: RefType
    turn_index: int
    ref_index: int


type RefType = Lit['search', 'image', 'view', 'news', 'fetch', 'academia']


class Item(Model):
    title: str
    url: str
    thumbnail_url: str | None = None
    pub_date: float | None
    snippet: str | None = None
    hue: None = None
    attributions: None = None
    attributions_debug: None = None
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
    attribution: str | None = None


class Size(Model):
    width: int
    height: int
