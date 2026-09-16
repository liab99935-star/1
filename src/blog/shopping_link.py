"""본문 주제와 어울리는 상품을 네이버 쇼핑 검색 API로 찾아 링크를 만든다.

네이버 쇼핑 검색 API는 블로그 API와 같은 Client ID/Secret을 쓰되,
개발자센터 앱 설정에서 "검색" API 사용 체크가 추가로 필요하다.

주의: 이 링크는 "네이버쇼핑 검색 결과 링크"이며, 클릭당/구매당 수익이 발생하는
진짜 제휴(파트너스) 링크가 되려면 별도로 "네이버 파트너스"에 가입하고
발급받은 제휴 링크로 감싸야 한다. NAVER_PARTNER_ID가 설정되어 있으면
간단한 파트너스 트래킹 파라미터를 붙이고, 없으면 일반 검색 링크만 사용한다.
"""
import requests
import config

SEARCH_URL = "https://openapi.naver.com/v1/search/shop.json"


def get_product_link_html(product_keyword: str) -> str:
    if not product_keyword or not config.NAVER_CLIENT_ID or not config.NAVER_CLIENT_SECRET:
        return ""

    headers = {
        "X-Naver-Client-Id": config.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET,
    }
    try:
        resp = requests.get(
            SEARCH_URL,
            headers=headers,
            params={"query": product_keyword, "display": 1, "sort": "sim"},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            return ""
        item = items[0]
        title = item["title"].replace("<b>", "").replace("</b>", "")
        link = item["link"]
        if config.NAVER_PARTNER_ID:
            sep = "&" if "?" in link else "?"
            link = f"{link}{sep}NaPm={config.NAVER_PARTNER_ID}"
        price = item.get("lprice", "")
        price_text = f" - {int(price):,}원~" if price else ""
        return f'<p>🛒 관련 추천 상품: <a href="{link}" target="_blank">{title}</a>{price_text}</p>'
    except Exception:
        return ""
