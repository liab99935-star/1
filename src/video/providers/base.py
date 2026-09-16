"""모든 영상 생성 프로바이더가 따라야 하는 공통 인터페이스.

나중에 Runway/Luma/Kling 중 하나를 실제로 쓰기로 정하면,
providers/ 아래에 파일 하나 추가하고 video/__init__.py의 get_provider()에 등록만 하면 된다.
"""
from abc import ABC, abstractmethod


class VideoProvider(ABC):
    @abstractmethod
    def generate_video(self, prompt: str, output_path: str) -> str:
        """prompt로 영상을 생성해 output_path에 저장하고, 최종 경로(또는 URL)를 반환한다."""
        raise NotImplementedError
