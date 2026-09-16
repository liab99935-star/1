# 블로그·인스타·영상 콘텐츠 자동 생성기

매일 트렌드 키워드를 기반으로

- **네이버 블로그** 글 (자동 업로드 가능)
- **인스타그램** 캡션 + 해시태그 (업로드는 수동)
- **저장/공유가 잘 되는 숏폼 영상** 기획 + AI 영상 생성

을 한 번에 만들어주는 자동화 도구입니다.

API 키가 하나도 없어도 일단 실행됩니다 — 실제 콘텐츠 대신 `[예시 콘텐츠]`라고 표시된
미리보기가 생성되어, 결과물의 형태를 먼저 확인할 수 있습니다. 키를 하나씩 채울 때마다
해당 부분만 실제 자동화로 바뀝니다.

## 왜 "네이버 인기 검색어 자동 수집"이 아니라 구글 트렌드인가요?

네이버는 2021년에 실시간 급상승 검색어 서비스를 공식 폐지했고, 지금의 네이버 데이터랩 API는
"내가 지정한 키워드"의 검색량 추이만 보여줄 뿐, 오늘의 인기 키워드를 스스로 찾아주지는
않습니다. 그래서 이 프로젝트는 **구글 트렌드(대한민국) 일별 인기 검색어**를 기본 키워드
소스로 사용합니다 (`src/trends/google_trends.py`). 원하는 키워드를 직접 쓰고 싶다면
`--keyword` 옵션으로 언제든 지정할 수 있습니다.

## 1. 설치

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows는 .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## 2. 바로 테스트 (키 없이)

```bash
python main.py run --keyword "다이어트 식단"
```

`output/오늘날짜/` 폴더에 블로그 글, 인스타 캡션, 영상 기획서가 생성됩니다. (아직은 예시 콘텐츠)

## 3. 실제 자동화로 전환하기

### 3-1. 블로그/인스타 글쓰기 AI (OpenAI API)

ChatGPT 무료/Plus 구독과 API는 별개 상품입니다. 아래에서 API 키를 발급받아야
프로그램이 자동으로 글을 씁니다. (사용한 만큼만 과금, 소액)

1. https://platform.openai.com/api-keys 접속 후 로그인
2. "Create new secret key" 클릭 → 키 복사
3. https://platform.openai.com/settings/organization/billing 에서 최소 금액 충전
4. `.env` 파일의 `OPENAI_API_KEY=` 뒤에 붙여넣기

### 3-2. 네이버 블로그 자동 업로드

1. https://developers.naver.com/apps 접속 → "애플리케이션 등록"
2. 사용 API에서 **"네이버 로그인"**, **"블로그"** 둘 다 체크
3. 서비스 URL, Callback URL은 `http://localhost:8080/callback` 로 등록
4. 등록 후 나오는 **Client ID / Client Secret**을 `.env`에 입력
5. 아래 명령으로 로그인 토큰을 한 번 발급받기:
   ```bash
   python scripts/get_naver_token.py
   ```
   브라우저가 열리면 네이버 로그인 → 동의 → 콘솔에 뜨는 토큰을 `.env`의
   `NAVER_ACCESS_TOKEN`에 붙여넣기
6. `.env`의 `NAVER_BLOG_ID`에 본인 블로그 주소의 아이디 부분 입력
   (`blog.naver.com/이 부분`)
7. 이제부터 `--publish-blog` 옵션을 주면 실제로 업로드됩니다:
   ```bash
   python main.py run --publish-blog
   ```
   옵션 없이 실행하면 파일로만 저장되고 업로드는 되지 않습니다 (안전을 위한 기본값).

> 참고: 네이버 access token은 보통 짧은 유효기간을 가집니다. 토큰이 만료되면
> `scripts/get_naver_token.py`를 다시 실행해서 재발급하세요. 매일 자동 업로드까지
> 완전히 무인화하려면 refresh token 로직 추가가 필요합니다 — 필요하면 요청해주세요.

### 3-3. AI 영상 생성 API

아직 어떤 서비스를 쓸지 정하지 않으셨다면 `VIDEO_PROVIDER=mock` 상태로 두면 됩니다
(영상 기획서는 정상적으로 생성되고, 실제 영상 파일 대신 안내 텍스트가 생깁니다).

정하시면:

| 서비스 | 특징 | .env 설정 |
|---|---|---|
| Runway (Gen-3/4) | 이미지/텍스트 기반 고품질 영상, 유료 | `VIDEO_PROVIDER=runway`, `RUNWAY_API_KEY` |
| Luma Dream Machine | 자연스러운 카메라 무빙 | `VIDEO_PROVIDER=luma`, `LUMA_API_KEY` |
| Kling AI | 긴 길이(최대 2분) 지원 | `VIDEO_PROVIDER=kling`, `KLING_API_KEY` |

각 서비스 홈페이지에서 API 키 발급 후 `.env`에 넣으면 바로 전환됩니다.
API 스펙은 자주 바뀌므로, 연동 코드(`src/video/providers/`)의 주석에 적힌 공식 문서
링크로 실제 사용 전에 한 번 더 확인하는 것을 권장합니다.

## 4. 매일 자동으로 실행되게 하기 (스케줄링)

코딩에 익숙하지 않다면, 운영체제의 "정해진 시간에 명령어 실행" 기능을 쓰는 게 가장 쉽습니다.

**macOS / Linux (cron)**

```bash
crontab -e
# 매일 오전 9시에 실행 (경로는 본인 환경에 맞게 수정)
0 9 * * * cd /home/user/1 && .venv/bin/python main.py run --publish-blog >> log.txt 2>&1
```

**Windows (작업 스케줄러)**

1. "작업 스케줄러" 실행 → "기본 작업 만들기"
2. 트리거: 매일, 원하는 시간
3. 동작: 프로그램 시작
   - 프로그램: `C:\경로\.venv\Scripts\python.exe`
   - 인수: `main.py run --publish-blog`
   - 시작 위치: 프로젝트 폴더 경로

## 5. 결과물 구조

```
output/2026-09-16/
├── blog_title.txt      # 블로그 제목
├── blog.html            # 블로그 본문 (네이버 블로그에 그대로 붙여넣기 가능)
├── blog_tags.txt        # 블로그 태그
├── instagram.txt        # 인스타 캡션 + 해시태그 (직접 앱에서 업로드)
├── video_plan.json      # 영상 기획 (훅, 장면별 대본, 저장유도 문구, 영상생성 프롬프트)
└── video.mp4 (또는 video.mock.txt)
```

인스타그램은 요청하신 대로 **콘텐츠 생성까지만** 자동화되어 있고, 실제 게시는 앱에서
직접 하시면 됩니다. (Instagram Graph API를 통한 완전 자동 게시를 원하시면 비즈니스 계정
전환과 Meta 앱 심사가 필요합니다 — 나중에 원하시면 추가해드릴 수 있어요.)

## 6. 프로젝트 구조

```
config.py                      # .env 값을 읽어 전역 설정으로 노출
main.py                        # 실행 진입점 (CLI)
src/
├── trends/google_trends.py    # 오늘의 트렌드 키워드
├── text_ai/openai_client.py   # OpenAI 호출 공통 래퍼 (키 없으면 예시 텍스트 반환)
├── blog/
│   ├── writer.py               # 블로그 글 생성
│   └── naver_poster.py         # 네이버 블로그 업로드
├── instagram/content_generator.py  # 인스타 캡션/해시태그 생성
└── video/
    ├── planner.py               # 영상 기획(훅/대본/씬 분해)
    └── providers/                # Runway/Luma/Kling/Mock 프로바이더 (플러그인 구조)
scripts/get_naver_token.py     # 네이버 OAuth 토큰 1회 발급 도우미
```
