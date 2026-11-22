from fastapi import FastAPI, HTTPException
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse
from app.services.analysis_service import build_analysis
from app.services.website_extractor import extract_website

app = FastAPI(
    title=settings.app_name,
    description="Extracts public website content and generates AI-powered business, competitor, SEO and audience insights.",
    version="1.0.0",
)


@app.get("/")
@app.get("/health")
@app.get("/health-check")
async def health_check():
    return {"status": "ok", "message": "AI Website Link Analysis API is running"}


## Analysis url data ####
@app.post("/link-analysis", response_model=LinkAnalysisResponse)
async def link_analysis(payload: LinkAnalysisRequest):
    try:
        website_data = await extract_website(str(payload.url))
        return await run_in_threadpool(build_analysis, str(payload.url), website_data)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc.__class__.__name__}.")
