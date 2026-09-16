import config


def get_provider():
    provider = config.VIDEO_PROVIDER.lower()

    if provider == "runway" and config.RUNWAY_API_KEY:
        from src.video.providers.runway_provider import RunwayProvider

        return RunwayProvider(config.RUNWAY_API_KEY)

    if provider == "luma" and config.LUMA_API_KEY:
        from src.video.providers.luma_provider import LumaProvider

        return LumaProvider(config.LUMA_API_KEY)

    if provider == "kling" and config.KLING_API_KEY:
        from src.video.providers.kling_provider import KlingProvider

        return KlingProvider(config.KLING_API_KEY)

    from src.video.providers.mock_provider import MockProvider

    return MockProvider()
