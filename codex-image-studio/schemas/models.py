from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field


GenerationMode = Literal["single-poster", "multi-page-carousel", "topic-batch"]


class GenerationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    creator_name: str = ""
    platform: str = "xhs"
    topic: str
    angle: str = ""
    generation_mode: GenerationMode = "multi-page-carousel"
    page_count: int = 5
    user_constraints: List[str] = Field(default_factory=list)
    target_audience: List[str] = Field(default_factory=list)


class GeneratedTitleSet(BaseModel):
    model_config = ConfigDict(extra="allow")

    primary_title: str
    alternatives: List[str] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)


class GeneratedCopySet(BaseModel):
    model_config = ConfigDict(extra="allow")

    opening_hook: str = ""
    main_body: str = ""
    step_blocks: List[str] = Field(default_factory=list)
    closing_cta: str = ""
    hashtags: List[str] = Field(default_factory=list)


class ImagePrompt(BaseModel):
    model_config = ConfigDict(extra="allow")

    page_number: int
    page_role: str
    prompt: str
    negative_prompt: str = ""
    layout_notes: List[str] = Field(default_factory=list)
    copy_overlay: str = ""


class ImagePromptSet(BaseModel):
    model_config = ConfigDict(extra="allow")

    prompts: List[ImagePrompt] = Field(default_factory=list)


class PagePlan(BaseModel):
    model_config = ConfigDict(extra="allow")

    page_number: int
    page_role: str
    goal: str
    copy_summary: str = ""
    visual_summary: str = ""


class PostLayoutPlan(BaseModel):
    model_config = ConfigDict(extra="allow")

    generation_mode: GenerationMode
    pages: List[PagePlan] = Field(default_factory=list)


class GeneratedPostBundle(BaseModel):
    model_config = ConfigDict(extra="allow")

    request: GenerationRequest
    titles: GeneratedTitleSet
    copy_set: GeneratedCopySet
    image_prompts: ImagePromptSet
    layout_plan: PostLayoutPlan
    generated_at: datetime
    notes: str = ""


GenerationRequest.model_rebuild()
GeneratedTitleSet.model_rebuild()
GeneratedCopySet.model_rebuild()
ImagePrompt.model_rebuild()
ImagePromptSet.model_rebuild()
PagePlan.model_rebuild()
PostLayoutPlan.model_rebuild()
GeneratedPostBundle.model_rebuild()
