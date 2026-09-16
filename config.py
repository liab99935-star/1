import os
from dotenv import load_dotenv

load_dotenv()


def _get(name, default=""):
    return os.getenv(name, default).strip()


OPENAI_API_KEY = _get("OPENAI_API_KEY")
OPENAI_MODEL = _get("OPENAI_MODEL", "gpt-4o-mini")

NAVER_CLIENT_ID = _get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = _get("NAVER_CLIENT_SECRET")
NAVER_ACCESS_TOKEN = _get("NAVER_ACCESS_TOKEN")
NAVER_BLOG_ID = _get("NAVER_BLOG_ID")

VIDEO_PROVIDER = _get("VIDEO_PROVIDER", "mock")
RUNWAY_API_KEY = _get("RUNWAY_API_KEY")
LUMA_API_KEY = _get("LUMA_API_KEY")
KLING_API_KEY = _get("KLING_API_KEY")

HAS_TEXT_AI = bool(OPENAI_API_KEY)
HAS_NAVER_AUTH = bool(NAVER_ACCESS_TOKEN and NAVER_BLOG_ID)
