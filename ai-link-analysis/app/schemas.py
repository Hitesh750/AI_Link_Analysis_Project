from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class LinkAnalysisRequest(BaseModel):
    url: HttpUrl


class Competitor(BaseModel):
    brand_name: str
    overview: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses_or_gaps: List[str] = Field(default_factory=list)
    evidence_status: str = Field(
        default="AI-suggested/unverified",
        description=(
            "Indicates the verification status of the competitor information. "
            "Use 'verified' only when supported by credible fetched sources. "
            "Otherwise, use 'AI-suggested/unverified'."
        ),
    )



class CompetitorAnalysis(BaseModel):
    brand_name: str
    brand_overview: str
    business_category: str
    main_products_and_services: List[str]
    competitors: List[Competitor]
    your_brand_strengths: List[str]
    competitive_advantages: List[str]
    opportunities: List[str]


class SearchQuery(BaseModel):
    query: str
    platforms: List[str]
    intent: str
    business_relevance: str
    target_audience: str


class SEOImprovements(BaseModel):
    primary_keyword: str
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    business_keywords: List[str]
    recommended_title: str
    title_primary_keyword: str
    title_structure: str
    meta_description: str
    supporting_content: List[str]


class Service(BaseModel):
    service_name: str
    description: str
    target_industry: str
    target_customer: str
    main_benefit: str
    identification: str = Field(description="Use 'Found on website' or 'Inferred recommendation'")


class AudienceSegment(BaseModel):
    audience: str
    business_type: str
    requirement: str
    customer_profile: str
    interests: List[str] = Field(default_factory=list)


class TargetAudience(BaseModel):
    primary_audience: List[AudienceSegment]
    secondary_audience: List[AudienceSegment]
    industries: List[str]
    business_types: List[str]
    geographical_focus: str
    customer_needs: List[str]
    marketing_segments: List[str]


class Brand(BaseModel):
    name: str
    category: str
    summary: str


class Analysis(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[SearchQuery] = Field(min_length=5, max_length=5)
    seo_improvements: SEOImprovements
    top_services: List[Service]
    target_audience: TargetAudience


class LinkAnalysisResponse(BaseModel):
    success: bool = True
    website: str
    brand: Brand
    analysis: Analysis
    extraction_notes: List[str] = Field(default_factory=list)
