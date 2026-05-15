from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Confidence = Literal["observed", "inferred", "uncertain"]


class RuleEvidence(BaseModel):
    model_config = ConfigDict(extra="allow")

    description: str
    example_refs: List[str] = Field(default_factory=list)
    confidence: Confidence = "observed"


class PositioningModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    role_identity: str = ""
    target_audience: List[str] = Field(default_factory=list)
    promise: str = ""
    authority_style: str = ""
    tone: str = ""
    complexity_level: str = ""
    evidence: List[RuleEvidence] = Field(default_factory=list)


class TitleModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    primary_patterns: List[str] = Field(default_factory=list)
    opening_components: List[str] = Field(default_factory=list)
    promise_style: str = ""
    urgency_level: str = ""
    emotion_level: str = ""
    instruction_density: str = ""
    common_lengths: List[str] = Field(default_factory=list)
    forbidden_patterns: List[str] = Field(default_factory=list)
    evidence: List[RuleEvidence] = Field(default_factory=list)


class CopyModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    opening_style: str = ""
    structure_templates: List[str] = Field(default_factory=list)
    explanation_style: str = ""
    step_density: str = ""
    list_density: str = ""
    cta_style: str = ""
    ending_patterns: List[str] = Field(default_factory=list)
    evidence: List[RuleEvidence] = Field(default_factory=list)


class VisualStyleModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    visual_archetype: str = ""
    color_system: List[str] = Field(default_factory=list)
    material_style: str = ""
    border_system: str = ""
    decorative_grammar: List[str] = Field(default_factory=list)
    layout_grammar: List[str] = Field(default_factory=list)
    information_density: str = ""
    typography_feel: str = ""
    image_subject_type: str = ""
    evidence: List[RuleEvidence] = Field(default_factory=list)


class PostingStrategyModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    publish_rhythm: str = ""
    frequency_hint: str = ""
    timing_preferences: List[str] = Field(default_factory=list)
    topic_clusters: List[str] = Field(default_factory=list)
    series_patterns: List[str] = Field(default_factory=list)
    evidence: List[RuleEvidence] = Field(default_factory=list)


class ConversionModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    follow_hooks: List[str] = Field(default_factory=list)
    save_hooks: List[str] = Field(default_factory=list)
    comment_hooks: List[str] = Field(default_factory=list)
    private_domain_paths: List[str] = Field(default_factory=list)
    homepage_redirects: List[str] = Field(default_factory=list)
    evidence: List[RuleEvidence] = Field(default_factory=list)


class MonetizationModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    visible_offers: List[str] = Field(default_factory=list)
    inferred_offer_type: List[str] = Field(default_factory=list)
    acquisition_role: str = ""
    trust_building_role: str = ""
    conversion_role: str = ""
    evidence: List[RuleEvidence] = Field(default_factory=list)


class ContentKnowledgeKB(BaseModel):
    model_config = ConfigDict(extra="allow")

    creator_name: str
    platform: str
    source_posts_analyzed: int = 0
    knowledge_domains: List[str] = Field(default_factory=list)
    topic_clusters: List[str] = Field(default_factory=list)
    recurring_concepts: List[str] = Field(default_factory=list)
    reusable_explanations: List[str] = Field(default_factory=list)
    cross_domain_mappings: List[str] = Field(default_factory=list)
    content_templates: List[str] = Field(default_factory=list)
    question_space: List[str] = Field(default_factory=list)
    evidence: List[RuleEvidence] = Field(default_factory=list)


class VisualPromptKernel(BaseModel):
    model_config = ConfigDict(extra="allow")

    creator_name: str
    platform: str
    style_name: str = ""
    base_style: str = ""
    palette_tokens: List[str] = Field(default_factory=list)
    layout_grammar: List[str] = Field(default_factory=list)
    typography_tokens: List[str] = Field(default_factory=list)
    decorative_grammar: List[str] = Field(default_factory=list)
    composition_rules: List[str] = Field(default_factory=list)
    information_density: str = ""
    prompt_seed: str = ""
    negative_prompt: str = ""
    reference_images: List[str] = Field(default_factory=list)
    evidence: List[RuleEvidence] = Field(default_factory=list)


class BehaviorDNA(BaseModel):
    model_config = ConfigDict(extra="allow")

    creator_name: str
    platform: str
    identity_core: str = ""
    promise_core: str = ""
    tone_core: str = ""
    title_core: List[str] = Field(default_factory=list)
    copy_core: List[str] = Field(default_factory=list)
    visual_core: List[str] = Field(default_factory=list)
    funnel_core: List[str] = Field(default_factory=list)
    monetization_core: List[str] = Field(default_factory=list)


class AccountBrainMeta(BaseModel):
    model_config = ConfigDict(extra="allow")

    generated_at: datetime
    input_completeness: str = ""
    total_posts_analyzed: int = 0
    total_visuals_analyzed: int = 0
    notes: str = ""


class AccountBrainBundle(BaseModel):
    model_config = ConfigDict(extra="allow")

    creator_name: str
    platform: str
    behavior_dna: BehaviorDNA
    positioning_model: PositioningModel
    title_model: TitleModel
    copy_model: CopyModel
    visual_style_model: VisualStyleModel
    posting_strategy_model: PostingStrategyModel
    conversion_model: ConversionModel
    monetization_model: MonetizationModel
    meta: AccountBrainMeta


class LearningAssetsBundle(BaseModel):
    model_config = ConfigDict(extra="allow")

    creator_name: str
    platform: str
    content_knowledge_kb: ContentKnowledgeKB
    visual_prompt_kernel: VisualPromptKernel
    meta: AccountBrainMeta


PositioningModel.model_rebuild()
TitleModel.model_rebuild()
CopyModel.model_rebuild()
VisualStyleModel.model_rebuild()
PostingStrategyModel.model_rebuild()
ConversionModel.model_rebuild()
MonetizationModel.model_rebuild()
ContentKnowledgeKB.model_rebuild()
VisualPromptKernel.model_rebuild()
BehaviorDNA.model_rebuild()
AccountBrainMeta.model_rebuild()
AccountBrainBundle.model_rebuild()
LearningAssetsBundle.model_rebuild()
