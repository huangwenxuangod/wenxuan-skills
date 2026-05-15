from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


Completeness = Literal["high", "partial", "low"]


class ContactMethod(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    value: str
    note: Optional[str] = None


class MetricSet(BaseModel):
    model_config = ConfigDict(extra="allow")

    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    favorites: Optional[int] = None


class AuthorRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    platform: str
    display_name: str = ""
    handle: str = ""
    profile_url: Optional[HttpUrl] = None
    verified: Optional[bool] = None


class AccountProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    platform: str
    display_name: str
    handle: str = ""
    bio: str = ""
    profile_url: Optional[HttpUrl] = None
    avatar_url: Optional[HttpUrl] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    like_count: Optional[int] = None
    verified: Optional[bool] = None
    aliases: List[str] = Field(default_factory=list)
    external_links: List[str] = Field(default_factory=list)
    contact_methods: List[ContactMethod] = Field(default_factory=list)
    discovered_from: List[str] = Field(default_factory=list)


class PostItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    platform: str
    post_id: str
    post_type: str
    title: str = ""
    subtitle: str = ""
    cover_text: str = ""
    first_sentence: str = ""
    body: str = ""
    transcript: str = ""
    published_at: Optional[datetime] = None
    source_url: Optional[HttpUrl] = None
    media_urls: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    metrics: MetricSet = Field(default_factory=MetricSet)
    author: Optional[AuthorRef] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VisualAsset(BaseModel):
    model_config = ConfigDict(extra="allow")

    asset_type: str
    source_url: Optional[HttpUrl] = None
    dominant_colors: List[str] = Field(default_factory=list)
    layout_guess: str = ""
    typography_guess: str = ""
    decorative_elements: List[str] = Field(default_factory=list)
    visual_notes: str = ""
    related_post_id: str = ""


class CommentSignal(BaseModel):
    model_config = ConfigDict(extra="allow")

    signal_type: str
    signal_text: str
    frequency_hint: str = ""
    representative_examples: List[str] = Field(default_factory=list)


class TrafficHook(BaseModel):
    model_config = ConfigDict(extra="allow")

    hook_type: str
    hook_text: str
    destination: str = ""
    confidence: str = ""


class MonetizationClue(BaseModel):
    model_config = ConfigDict(extra="allow")

    clue_type: str
    clue_text: str
    destination: str = ""
    confidence: str = ""


class FailedProvider(BaseModel):
    model_config = ConfigDict(extra="allow")

    provider: str
    error: str


class CaptureMeta(BaseModel):
    model_config = ConfigDict(extra="allow")

    attempted_providers: List[str] = Field(default_factory=list)
    failed_providers: List[FailedProvider] = Field(default_factory=list)
    captured_count: int = 0
    captured_at: datetime
    completeness: Completeness
    notes: str = ""


class CaptureBundle(BaseModel):
    model_config = ConfigDict(extra="allow")

    query: str
    task_type: str
    platform_hint: str = ""
    creator_hint: str = ""
    success: bool
    account_profile: Optional[AccountProfile] = None
    posts: List[PostItem] = Field(default_factory=list)
    visual_assets: List[VisualAsset] = Field(default_factory=list)
    comment_signals: List[CommentSignal] = Field(default_factory=list)
    traffic_hooks: List[TrafficHook] = Field(default_factory=list)
    monetization_clues: List[MonetizationClue] = Field(default_factory=list)
    related_links: List[str] = Field(default_factory=list)
    capture_meta: CaptureMeta
    error: Optional[str] = None


AccountProfile.model_rebuild()
PostItem.model_rebuild()
VisualAsset.model_rebuild()
CommentSignal.model_rebuild()
TrafficHook.model_rebuild()
MonetizationClue.model_rebuild()
CaptureMeta.model_rebuild()
CaptureBundle.model_rebuild()
