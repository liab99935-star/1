"""네이버 로그인 OAuth로 블로그 글쓰기용 ACCESS TOKEN을 한 번만 발급받는 도우미 스크립트.

사용법:
1. .env에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET을 먼저 채운다.
2. 네이버 개발자센터(https://developers.naver.com/apps) 앱 설정에서
   콜백 URL을 아래 REDIRECT_URI와 동일하게 등록한다.
3. 터미널에서 `python scripts/get_naver_token.py` 실행
4. 자동으로 뜨는 안내 링크를 브라우저에서 열어 네이버 로그인/동의
5. 콘솔에 출력되는 ACCESS TOKEN을 .env의 NAVER_ACCESS_TOKEN에 붙여넣는다.
6. NAVER_BLOG_ID(blog.naver.com/본인아이디의 그 아이디)도 .env에 채운다.
"""
import http.server
import urllib.parse
import webbrowser
import secrets

import requests

import config

REDIRECT_URI = "http://localhost:8080/callback"
AUTHORIZE_URL = "https://nid.naver.com/oauth2.0/authorize"
TOKEN_URL = "https://nid.naver.com/oauth2.0/token"

_captured_code = {}


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        _captured_code["code"] = qs.get("code", [None])[0]
        _captured_code["state"] = qs.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h2>인증 완료! 이 창은 닫고 터미널로 돌아가세요.</h2>".encode("utf-8"))

    def log_message(self, fmt, *args):
        pass  # 콘솔 로그 조용히 처리


def main():
    if not config.NAVER_CLIENT_ID or not config.NAVER_CLIENT_SECRET:
        print("먼저 .env 파일에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET을 채워주세요.")
        return

    state = secrets.token_hex(8)
    params = {
        "response_type": "code",
        "client_id": config.NAVER_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }
    auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    print("아래 주소를 브라우저에서 열어 네이버 로그인/동의를 진행하세요:")
    print(auth_url)
    webbrowser.open(auth_url)

    server = http.server.HTTPServer(("localhost", 8080), _CallbackHandler)
    print("\n로그인 완료를 기다리는 중... (브라우저에서 동의를 눌러주세요)")
    server.handle_request()  # 콜백 1회만 받고 종료

    code = _captured_code.get("code")
    returned_state = _captured_code.get("state")
    if not code or returned_state != state:
        print("인증 코드 수신 실패. 다시 시도해주세요.")
        return

    token_params = {
        "grant_type": "authorization_code",
        "client_id": config.NAVER_CLIENT_ID,
        "client_secret": config.NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }
    resp = requests.get(TOKEN_URL, params=token_params, timeout=15)
    resp.raise_for_status()
    token_data = resp.json()

    access_token = token_data.get("access_token")
    if not access_token:
        print("토큰 발급 실패:", token_data)
        return

    print("\n발급 성공! 아래 값을 .env 파일의 NAVER_ACCESS_TOKEN에 붙여넣으세요:\n")
    print(access_token)


if __name__ == "__main__":
    main()
