"""Kling AI API 연동.

주의: API 스펙은 자주 바뀝니다. 실제 사용 전 공식 문서(https://docs.qingque.cn 등,
지역/버전에 따라 문서 위치가 다를 수 있음)와 최신 엔드포인트를 반드시 대조하세요.
"""
import time
import requests
from src.video.providers.base import VideoProvider

API_BASE = "https://api-singapore.klingai.com/v1"


class KlingProvider(VideoProvider):
    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def generate_video(self, prompt: str, output_path: str) -> str:
        create_resp = requests.post(
            f"{API_BASE}/videos/text2video",
            headers=self.headers,
            json={"model_name": "kling-v1", "prompt": prompt, "duration": "5"},
            timeout=30,
        )
        create_resp.raise_for_status()
        task_id = create_resp.json()["data"]["task_id"]

        for _ in range(60):
            status_resp = requests.get(
                f"{API_BASE}/videos/text2video/{task_id}", headers=self.headers, timeout=15
            )
            status_resp.raise_for_status()
            data = status_resp.json()["data"]
            if data.get("task_status") == "succeed":
                video_url = data["task_result"]["videos"][0]["url"]
                video_bytes = requests.get(video_url, timeout=60).content
                with open(output_path, "wb") as f:
                    f.write(video_bytes)
                return output_path
            if data.get("task_status") == "failed":
                raise RuntimeError(f"Kling 영상 생성 실패: {data}")
            time.sleep(5)

        raise TimeoutError("Kling 영상 생성 시간 초과")
