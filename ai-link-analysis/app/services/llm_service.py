from google import genai
from google.genai import types
from fastapi import HTTPException

from app.config import settings
from app.schemas import Analysis


SYSTEM_INSTRUCTIONS = """
You are a careful business, SEO and audience analyst. Analyze only the supplied website evidence.
Do not invent facts, customer counts, revenue, search volumes, rankings, awards, locations or competitor claims.
If competitor information is not directly evidenced, provide plausible competitor categories/names only as AI suggestions
and explicitly mark evidence_status as 'AI-suggested; not independently verified'. Do not pretend to have browsed competitors.
Identify website services from page evidence where possible. Mark extrapolated services 'Inferred recommendation'.
Return exactly five relevant search queries, each with suitable platforms selected from Google Search, Facebook,
Instagram, LinkedIn and X (Twitter). Do not provide search-volume figures.
Provide up to five important services; use fewer if the website supports fewer.
If information is unavailable, say so clearly rather than guessing. Keep recommendations specific to the website.
""".strip()


def analyze_with_gemini(website_data: dict) -> Analysis:
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="Gemini API key is not configured. Set GEMINI_API_KEY in .env.")

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""{SYSTEM_INSTRUCTIONS}

Analyze this extracted website information:
URL: {website_data.get('final_url')}
Page title: {website_data.get('title')}
Meta description: {website_data.get('meta_description')}
Headings: {website_data.get('headings')}
Visible page text: {website_data.get('page_text')}

Return the full analysis in the required schema, including the actual brand_name if identifiable. The submitted website is the user's brand.
"""
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis,
                temperature=0.2,
            ),
        )
        if not response.text:
            raise ValueError("Gemini returned an empty response")
        return Analysis.model_validate_json(response.text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc.__class__.__name__}.")
