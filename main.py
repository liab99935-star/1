"""블로그/인스타 콘텐츠 + 영상 기획을 하루 한 번 자동 생성하는 진입점.

기본 사용법:
    python main.py run                     # 오늘의 트렌드 키워드로 전체 생성 (블로그는 파일 저장만, 자동 업로드 안 함)
    python main.py run --keyword "다이어트 식단"   # 키워드 직접 지정
    python main.py run --publish-blog       # 생성 후 네이버 블로그에 실제로 업로드까지 진행
"""
import argparse
import json
import os

from src.trends.google_trends import get_today_trending_keyword
from src.blog.writer import generate_blog_post
from src.blog.naver_poster import post_to_naver_blog
from src.instagram.content_generator import generate_instagram_content
from src.video.planner import generate_video_plan
from src.video import get_provider
from src.utils.storage import get_today_output_dir, save_text
import config


def run(keyword: str | None, publish_blog: bool):
    kw = keyword or get_today_trending_keyword()
    out_dir = get_today_output_dir()
    print(f"\n=== 오늘의 키워드: {kw} ===")
    print(f"결과 저장 폴더: {out_dir}\n")

    # 1. 블로그
    print("[1/3] 블로그 글 생성 중...")
    post = generate_blog_post(kw)
    save_text(out_dir, "blog_title.txt", post["title"])
    save_text(out_dir, "blog.html", post["body_html"])
    save_text(out_dir, "blog_tags.txt", ", ".join(post["tags"]))
    print(f"  -> 저장 완료: {out_dir}/blog.html")

    if publish_blog:
        if not config.HAS_NAVER_AUTH:
            print("  ! NAVER_ACCESS_TOKEN/NAVER_BLOG_ID 미설정으로 업로드를 건너뜁니다. (scripts/get_naver_token.py 먼저 실행)")
        else:
            try:
                result = post_to_naver_blog(post["title"], post["body_html"], post["tags"])
                print(f"  -> 네이버 블로그 업로드 완료: {result}")
            except Exception as e:
                print(f"  ! 네이버 블로그 업로드 실패: {e}")
    else:
        print("  (네이버 자동 업로드는 하지 않았습니다. --publish-blog 옵션을 주면 실제 업로드합니다)")

    # 2. 인스타그램
    print("\n[2/3] 인스타그램 콘텐츠 생성 중...")
    ig = generate_instagram_content(kw)
    ig_text = ig["caption"] + "\n\n" + " ".join(ig["hashtags"])
    save_text(out_dir, "instagram.txt", ig_text)
    print(f"  -> 저장 완료: {out_dir}/instagram.txt (직접 앱에서 업로드하세요)")

    # 3. 영상 기획 + 생성
    print("\n[3/3] 영상 기획 및 생성 중...")
    plan = generate_video_plan(kw)
    save_text(out_dir, "video_plan.json", json.dumps(plan, ensure_ascii=False, indent=2))

    provider = get_provider()
    video_path = os.path.join(out_dir, "video.mp4")
    try:
        result_path = provider.generate_video(plan.get("video_gen_prompt", kw), video_path)
        print(f"  -> 영상 결과: {result_path}")
    except Exception as e:
        print(f"  ! 영상 생성 실패: {e}")

    print(f"\n완료! '{out_dir}' 폴더를 확인하세요.")


def main():
    parser = argparse.ArgumentParser(description="블로그/인스타/영상 콘텐츠 자동 생성")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="오늘의 콘텐츠 생성")
    run_parser.add_argument("--keyword", type=str, default=None, help="키워드 직접 지정 (생략 시 오늘의 트렌드 자동 사용)")
    run_parser.add_argument("--publish-blog", action="store_true", help="생성 후 네이버 블로그에 실제로 업로드")

    args = parser.parse_args()

    if args.command == "run":
        run(args.keyword, args.publish_blog)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
