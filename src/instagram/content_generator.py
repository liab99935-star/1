"""인스타그램 캡션 + 해시태그 생성 (업로드는 수동이므로 텍스트 파일 생성까지만 담당)."""
from src.text_ai import openai_client

SYSTEM_PROMPT = """당신은 저장과 공유가 많이 되는 '효자 콘텐츠'를 만드는 인스타그램 마케터입니다.
원칙:
- 첫 줄에 스크롤을 멈추게 하는 훅(hook) 문장.
- 정보성/꿀팁형으로, 저장하고 싶게 만드는 실용적 내용 위주.
- 캡션 마지막에 "저장해두고 꼭 써보세요" 류의 저장 유도 문구를 자연스럽게 포함.
- 이모지는 과하지 않게 3~5개.
- 결과는 반드시 아래 JSON 형식으로만 출력한다.
{"caption": "...", "hashtags": ["#태그1", "#태그2", ...]}
hashtags는 10~15개, 대중적 태그와 니치 태그를 섞는다.
"""


def generate_instagram_content(keyword: str) -> dict:
    user_prompt = f"'{keyword}' 관련 저장/공유가 많이 될 인스타그램 게시글 캡션과 해시태그를 만들어줘."
    raw = openai_client.generate(SYSTEM_PROMPT, user_prompt, mock_label="인스타 캡션")

    import json

    try:
        data = json.loads(raw)
        return {
            "caption": data.get("caption", raw),
            "hashtags": data.get("hashtags", [f"#{keyword}"]),
        }
    except (json.JSONDecodeError, TypeError):
        return {"caption": raw, "hashtags": [f"#{keyword}"]}
