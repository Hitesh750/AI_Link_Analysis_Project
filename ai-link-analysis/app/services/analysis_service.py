from app.schemas import Brand, LinkAnalysisResponse
from app.services.llm_service import analyze_with_gemini


def build_analysis(url: str, website_data: dict) -> LinkAnalysisResponse:
    analysis = analyze_with_gemini(website_data)
    brand_name = analysis.competitor_analysis.brand_name or website_data.get("title") or "Business name not clearly identified"

    return LinkAnalysisResponse(
        success=True,
        website=website_data.get("final_url", url),
        brand=Brand(
            name=brand_name[:120],
            category=analysis.competitor_analysis.business_category,
            summary=analysis.competitor_analysis.brand_overview,
        ),
        analysis=analysis,
        extraction_notes=[
            "Analysis is based on publicly accessible text extracted from the submitted page.",
            "Competitor suggestions are not independently verified unless explicitly supported by source evidence.",
            "No search-volume or ranking data was queried or reported.",
        ],
    )
