"""블로그 본문에 넣을 사진을 Pixabay 무료 API로 검색한다.

https://pixabay.com/api/docs/ 에서 무료 API 키 발급 (가입만 하면 즉시 발급).
키가 없으면 이미지 없이 진행(place holder 문구만 남김).
"""
import requests
import config

SEARCH_URL = "https://pixabay.com/api/"


def get_image_urls(keywords: list[str]) -> list[str]:
    if not config.PIXABAY_API_KEY:
        return []

    urls = []
    for kw in keywords:
        try:
            resp = requests.get(
                SEARCH_URL,
                params={
                    "key": config.PIXABAY_API_KEY,
                    "q": kw,
                    "image_type": "photo",
                    "safesearch": "true",
                    "per_page": 3,
                },
                timeout=10,
            )
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            if hits:
                urls.append(hits[0]["webformatURL"])
        except Exception:
            continue
    return urls


def build_image_html(urls: list[str]) -> str:
    if not urls:
        return ""
    return "\n".join(f'<p><img src="{u}" alt="관련 이미지"/></p>' for u in urls)
