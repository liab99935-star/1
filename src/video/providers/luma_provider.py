"""Luma Dream Machine API 연동.

주의: API 스펙은 자주 바뀝니다. 실제 사용 전 https://docs.lumalabs.ai 최신 문서를
반드시 대조하세요.
"""
import time
import requests
from src.video.providers.base import VideoProvider

API_BASE = "https://api.lumalabs.ai/dream-machine/v1"


class LumaProvider(VideoProvider):
    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def generate_video(self, prompt: str, output_path: str) -> str:
        create_resp = requests.post(
            f"{API_BASE}/generations",
            headers=self.headers,
            json={"prompt": prompt},
            timeout=30,
        )
        create_resp.raise_for_status()
        gen_id = create_resp.json()["id"]

        for _ in range(60):
            status_resp = requests.get(f"{API_BASE}/generations/{gen_id}", headers=self.headers, timeout=15)
            status_resp.raise_for_status()
            data = status_resp.json()
            if data.get("state") == "completed":
                video_url = data["assets"]["video"]
                video_bytes = requests.get(video_url, timeout=60).content
                with open(output_path, "wb") as f:
                    f.write(video_bytes)
                return output_path
            if data.get("state") == "failed":
                raise RuntimeError(f"Luma 영상 생성 실패: {data}")
            time.sleep(5)

        raise TimeoutError("Luma 영상 생성 시간 초과")
