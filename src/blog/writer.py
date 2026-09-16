"""트렌드 키워드를 받아 네이버 블로그용 글을 생성한다."""
from src.text_ai import openai_client

SYSTEM_PROMPT = """당신은 네이버 블로그 상위노출과 체류시간에 강한 한국어 블로그 작가입니다.
아래 원칙을 지켜 글을 씁니다.
- 첫 문단에서 바로 궁금증을 해결해줄 것처럼 후킹한다.
- 소제목(##)으로 섹션을 나누고, 각 섹션은 3~5문장.
- 실생활에 바로 쓸 수 있는 구체적인 정보/팁/숫자를 포함한다.
- 과장 광고성 표현, 허위 정보 금지.
- 마지막에 요약 체크리스트를 넣는다.
- 결과는 반드시 아래 형식의 JSON으로만 출력한다.
{"title": "...", "body_html": "...", "tags": ["...", "..."]}
body_html은 네이버 블로그에 바로 붙여넣을 수 있는 간단한 HTML(문단은 <p>, 소제목은 <h3>)로 작성한다.
"""


def generate_blog_post(keyword: str) -> dict:
    user_prompt = f"오늘의 인기 키워드 '{keyword}'를 주제로 블로그 글을 작성해줘."
    raw = openai_client.generate(SYSTEM_PROMPT, user_prompt, mock_label="블로그 글")

    import json

    try:
        data = json.loads(raw)
        return {
            "title": data.get("title", keyword),
            "body_html": data.get("body_html", raw),
            "tags": data.get("tags", [keyword]),
        }
    except (json.JSONDecodeError, TypeError):
        # 목업 응답이거나 JSON 파싱 실패 시 있는 그대로 감싸서 반환
        return {
            "title": f"[예시] {keyword}",
            "body_html": f"<p>{raw}</p>",
            "tags": [keyword],
        }
