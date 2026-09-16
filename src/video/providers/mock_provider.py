from src.video.providers.base import VideoProvider


class MockProvider(VideoProvider):
    """영상 API를 아직 정하지 않았을 때 쓰는 기본 프로바이더.

    실제 영상 파일 대신, 어떤 프롬프트로 무엇이 생성되었을지 알 수 있는
    텍스트 placeholder 파일을 만든다.
    """

    def generate_video(self, prompt: str, output_path: str) -> str:
        placeholder_path = output_path.replace(".mp4", ".mock.txt")
        with open(placeholder_path, "w", encoding="utf-8") as f:
            f.write(
                "[MOCK 영상 - VIDEO_PROVIDER 미설정]\n"
                "실제 영상 API(Runway/Luma/Kling 등)를 정하고 .env에 키를 넣으면 "
                "이 자리에 실제 mp4가 생성됩니다.\n\n"
                f"사용될 프롬프트:\n{prompt}\n"
            )
        return placeholder_path
