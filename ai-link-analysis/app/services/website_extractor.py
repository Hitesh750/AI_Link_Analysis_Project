from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

from app.config import settings
from app.utils.validators import validate_public_url


def _clean_text(html: bytes, page_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript", "svg", "iframe", "canvas", "form"]):
        element.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else ""
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:30]]
    canonical_tag = soup.find("link", rel="canonical")
    canonical = urljoin(page_url, canonical_tag.get("href", "")) if canonical_tag and canonical_tag.get("href") else None
    text = " ".join(soup.stripped_strings)
    text = " ".join(text.split())[: settings.max_text_chars]

    return {
        "title": title,
        "meta_description": description,
        "headings": headings,
        "page_text": text,
        "canonical_url": canonical,
    }


async def extract_website(url: str) -> dict:
    current_url = validate_public_url(url)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; WebsiteAnalysisBot/1.0; +https://example.org/bot)"}

    async with httpx.AsyncClient(
        timeout=settings.request_timeout_seconds,
        follow_redirects=False,
        trust_env=False,
        headers=headers,
    ) as client:
        for _ in range(4):
            validate_public_url(current_url)  # Revalidate every redirect destination.
            try:
                async with client.stream("GET", current_url) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise HTTPException(status_code=502, detail="Website returned an invalid redirect.")
                        current_url = urljoin(current_url, location)
                        continue
                    if response.status_code >= 400:
                        raise HTTPException(status_code=502, detail=f"Website returned HTTP {response.status_code}.")
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        raise HTTPException(status_code=415, detail="The URL does not return an HTML page.")
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > settings.max_html_bytes:
                            raise HTTPException(status_code=413, detail="Website HTML is larger than the allowed limit.")
                    return _clean_text(bytes(body), current_url) | {"final_url": current_url}
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Timed out while fetching the website.")
            except httpx.RequestError as exc:
                raise HTTPException(status_code=502, detail=f"Could not access website: {exc.__class__.__name__}.")
        raise HTTPException(status_code=502, detail="Website redirected too many times.")
