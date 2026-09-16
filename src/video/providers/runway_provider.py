"""Runway API 연동 (Gen-3/Gen-4 계열, text/image-to-video).

주의: Runway API 스펙은 자주 바뀝니다. 아래는 2024년 하반기 기준 공개 문서를 참고한
best-effort 구현이므로, 실제 사용 전 https://docs.dev.runwayml.com 최신 문서와
엔드포인트/파라미터를 반드시 대조하세요.
"""
import time
import requests
from src.video.providers.base import VideoProvider

API_BASE = "https://api.dev.runwayml.com/v1"


class RunwayProvider(VideoProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06",
        }

    def generate_video(self, prompt: str, output_path: str) -> str:
        create_resp = requests.post(
            f"{API_BASE}/text_to_video",
            headers=self.headers,
            json={"promptText": prompt, "model": "gen3a_turbo", "duration": 5, "ratio": "768:1280"},
            timeout=30,
        )
        create_resp.raise_for_status()
        task_id = create_resp.json()["id"]

        for _ in range(60):  # 최대 5분 대기
            status_resp = requests.get(f"{API_BASE}/tasks/{task_id}", headers=self.headers, timeout=15)
            status_resp.raise_for_status()
            data = status_resp.json()
            if data.get("status") == "SUCCEEDED":
                video_url = data["output"][0]
                video_bytes = requests.get(video_url, timeout=60).content
                with open(output_path, "wb") as f:
                    f.write(video_bytes)
                return output_path
            if data.get("status") == "FAILED":
                raise RuntimeError(f"Runway 영상 생성 실패: {data}")
            time.sleep(5)

        raise TimeoutError("Runway 영상 생성 시간 초과")
