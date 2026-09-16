"""OpenAI API를 감싸는 얇은 래퍼.

API 키가 없으면 예외를 던지지 않고, 구조를 미리 확인할 수 있도록
"[예시 콘텐츠]" 표시가 붙은 목업 텍스트를 돌려준다.
"""
import config


def generate(system_prompt: str, user_prompt: str, mock_label: str = "콘텐츠") -> str:
    if not config.HAS_TEXT_AI:
        return (
            f"[예시 콘텐츠 - OPENAI_API_KEY 미설정]\n"
            f"실제 {mock_label}은(는) .env에 OPENAI_API_KEY를 넣으면 여기에 생성됩니다.\n"
            f"--- 요청 프롬프트 미리보기 ---\n{user_prompt[:300]}"
        )

    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
    )
    return resp.choices[0].message.content.strip()
