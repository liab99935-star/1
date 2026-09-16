"""'저장/공유가 많이 되는' 숏폼 영상 기획(훅, 대본, 장면 분해)을 생성한다."""
from src.text_ai import openai_client

SYSTEM_PROMPT = """당신은 릴스/쇼츠에서 저장과 공유 지표가 특히 높은 콘텐츠를 기획하는 PD입니다.
저장/공유가 잘 되는 콘텐츠의 공통점을 활용한다: 정보 밀도가 높은 꿀팁/리스트/노하우,
"이거 모르면 손해", "저장 필수" 류의 훅, 텍스트로도 이해되는 자막 중심 구성.
결과는 반드시 아래 JSON 형식으로만 출력한다.
{
  "hook": "영상 시작 3초 안에 나올 한 문장 훅",
  "scenes": [
    {"duration_sec": 3, "narration": "...", "visual": "화면에 보여줄 이미지/장면 묘사"},
    ...
  ],
  "cta": "영상 마지막 저장/공유 유도 문구",
  "video_gen_prompt": "AI 영상 생성 API에 넣을 영어 프롬프트 (스타일, 장면 묘사 포함)"
}
scenes는 15~30초 분량(5~8개 장면)으로 구성한다.
"""


def generate_video_plan(keyword: str) -> dict:
    user_prompt = f"'{keyword}' 주제로 저장/공유가 잘 되는 15~30초 숏폼 영상을 기획해줘."
    raw = openai_client.generate(SYSTEM_PROMPT, user_prompt, mock_label="영상 기획")

    import json

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {
            "hook": f"[예시] {keyword} 관련 훅",
            "scenes": [{"duration_sec": 5, "narration": raw, "visual": "예시 장면"}],
            "cta": "저장하고 나중에 다시 보세요!",
            "video_gen_prompt": f"{keyword}, informative short-form video, clean captions",
        }
