"""네이버 블로그 글쓰기 API 연동.

사전 준비 (README 참고):
1. https://developers.naver.com/apps 에서 앱 등록, "네이버 로그인" + "블로그" 사용 설정
2. scripts/get_naver_token.py 실행해서 NAVER_ACCESS_TOKEN 발급받아 .env에 저장
3. NAVER_BLOG_ID(블로그 아이디, blog.naver.com/<이 부분>)를 .env에 저장

토큰/블로그ID가 없으면 실제로 올리지 않고, 결과를 파일로만 저장하도록 상위 로직(main.py)에서 분기한다.
"""
import requests
import config

WRITE_POST_URL = "https://openapi.naver.com/blog/writePost.json"


def post_to_naver_blog(title: str, body_html: str, tags: list[str]) -> dict:
    if not config.HAS_NAVER_AUTH:
        raise RuntimeError(
            "NAVER_ACCESS_TOKEN 또는 NAVER_BLOG_ID가 설정되지 않았습니다. "
            "scripts/get_naver_token.py 로 먼저 토큰을 발급받으세요."
        )

    headers = {"Authorization": f"Bearer {config.NAVER_ACCESS_TOKEN}"}
    payload = {
        "title": title,
        "contents": body_html,
        "blogId": config.NAVER_BLOG_ID,
        "tag": ",".join(tags),
        "openyn": "Y",  # 공개 여부
        "categoryNo": "",  # 비워두면 기본 카테고리
    }
    resp = requests.post(WRITE_POST_URL, headers=headers, data=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()
