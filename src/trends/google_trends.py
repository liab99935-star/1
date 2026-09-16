"""오늘의 인기 키워드를 가져온다.

네이버는 2021년에 실시간 급상승 검색어 API/서비스를 공식 폐지했기 때문에
"오늘 인기 검색어"를 자동으로 뽑아주는 공식 API가 존재하지 않는다.
따라서 이 프로젝트는 구글 트렌드(대한민국) 일별 인기 검색어를 기본 소스로 쓴다.
pytrends는 구글 공식 API가 아닌 비공식 라이브러리라 가끔 응답이 막힐 수 있어,
실패 시 기본 키워드 목록으로 자동 대체(fallback)한다.
"""
from pytrends.request import TrendReq

FALLBACK_KEYWORDS = [
    "환절기 건강관리",
    "자취 요리 꿀팁",
    "집에서 돈 버는 법",
    "가성비 여행지 추천",
    "다이어트 식단",
]


def _fetch_trending_list() -> list[str]:
    try:
        pytrends = TrendReq(hl="ko-KR", tz=540)
        df = pytrends.trending_searches(pn="south_korea")
        keywords = df[0].tolist()
        if keywords:
            return keywords
    except Exception:
        pass
    return list(FALLBACK_KEYWORDS)


def get_today_trending_keyword(index: int = 0) -> str:
    """구글 트렌드 한국 일별 인기 검색어 중 하나를 반환. 실패하면 기본값 사용."""
    keywords = _fetch_trending_list()
    return keywords[index % len(keywords)]


def get_today_trending_keywords(n: int) -> list[str]:
    """오늘 쓸 키워드 n개를 반환한다. 실제 트렌드 개수가 모자라면 기본 키워드를 순환시켜 채운다."""
    pool = list(dict.fromkeys(_fetch_trending_list() + FALLBACK_KEYWORDS))  # 순서 유지 + 중복 제거
    return [pool[i % len(pool)] for i in range(n)]
