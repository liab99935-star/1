"""트렌드 키워드를 받아 네이버 블로그용 글을 생성한다."""
from src.text_ai import openai_client

SYSTEM_PROMPT = """당신은 네이버 블로그 홈(메인)피드 노출에 강한 한국어 블로그 작가입니다.
네이버 C-Rank/D.I.A 로직이 선호하는 아래 원칙을 지켜 글을 씁니다.
- 공백 포함 1500자 이상, 정보성 위주로 충실하게 작성한다 (분량을 채우기 위한 반복/늘리기 금지).
- 첫 문단에서 바로 궁금증을 해결해줄 것처럼 후킹한다.
- 소제목(##)으로 4~6개 섹션을 나누고, 각 섹션은 4~6문장으로 구체적인 정보/팁/숫자를 포함한다.
- 제목/본문에 동일 키워드를 부자연스럽게 반복하지 않는다 (키워드 스터핑 금지 - 저품질 판정 요인).
- 과장 광고성 표현, 허위/의료 효능 단정 표현 금지.
- 마지막에 요약 체크리스트를 넣는다.
- 결과는 반드시 아래 형식의 JSON으로만 출력한다.
{"title": "...", "body_html": "...", "tags": ["...", "..."], "image_keywords": ["...", "...", "..."], "product_keyword": "..."}
- body_html은 네이버 블로그에 바로 붙여넣을 수 있는 간단한 HTML(문단은 <p>, 소제목은 <h3>)로 작성한다. 이미지나 상품 링크 태그는 넣지 않는다 (별도로 삽입됨).
- image_keywords는 본문 내용과 어울리는 사진을 찾기 위한 영어 검색어 3개.
- product_keyword는 본문 주제와 자연스럽게 연결되는, 쇼핑 링크로 소개할 상품 검색어 1개 (없으면 빈 문자열).
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
            "image_keywords": data.get("image_keywords", [keyword]),
            "product_keyword": data.get("product_keyword", keyword),
        }
    except (json.JSONDecodeError, TypeError):
        # 목업 응답이거나 JSON 파싱 실패 시 있는 그대로 감싸서 반환
        return {
            "title": f"[예시] {keyword}",
            "body_html": f"<p>{raw}</p>",
            "tags": [keyword],
            "image_keywords": [keyword],
            "product_keyword": keyword,
        }
