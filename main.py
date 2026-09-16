"""블로그/인스타 콘텐츠 + 영상 기획을 하루 한 번 자동 생성하는 진입점.

기본 사용법:
    python main.py run                     # 오늘의 트렌드 키워드로 전체 생성 (블로그는 파일 저장만, 자동 업로드 안 함)
    python main.py run --keyword "다이어트 식단"   # 키워드 직접 지정
    python main.py run --publish-blog       # 생성 후 네이버 블로그에 실제로 업로드까지 진행

    python main.py blog                     # 하루 15개(기본값) 블로그 글을 이미지+쇼핑링크 포함해 생성
    python main.py blog --publish            # 생성 후 네이버 블로그에 실제로 업로드까지 진행
    python main.py blog --count 5 --interval-min 20   # 개수/발행 간격 직접 지정
"""
import argparse
import json
import os
import time

from src.trends.google_trends import get_today_trending_keyword, get_today_trending_keywords
from src.blog.writer import generate_blog_post
from src.blog.naver_poster import post_to_naver_blog
from src.blog.images import get_image_urls, build_image_html
from src.blog.shopping_link import get_product_link_html
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


def run_blog_batch(count: int, publish: bool, interval_min: float):
    keywords = get_today_trending_keywords(count)
    out_dir = get_today_output_dir()
    print(f"\n=== 오늘 발행할 블로그 글 {count}개 ===")
    print(f"결과 저장 폴더: {out_dir}\n")

    if publish and not config.HAS_NAVER_AUTH:
        print("! NAVER_ACCESS_TOKEN/NAVER_BLOG_ID 미설정 - 이번 실행은 파일 저장만 하고 업로드는 건너뜁니다.")
        print("  (scripts/get_naver_token.py 먼저 실행하세요)\n")
        publish = False

    for i, kw in enumerate(keywords, start=1):
        print(f"[{i}/{count}] 키워드: {kw}")
        post = generate_blog_post(kw)

        image_urls = get_image_urls(post["image_keywords"])
        image_html = build_image_html(image_urls)
        shopping_html = get_product_link_html(post["product_keyword"])

        # 첫 이미지는 글 도입부, 나머지 이미지+쇼핑 링크는 본문 뒤에 배치
        first_image = f'<p><img src="{image_urls[0]}" alt="{kw}"/></p>' if image_urls else ""
        rest_images = build_image_html(image_urls[1:]) if len(image_urls) > 1 else ""
        full_html = "\n".join(part for part in [first_image, post["body_html"], rest_images, shopping_html] if part)

        prefix = f"{i:02d}_{kw}"
        save_text(out_dir, f"{prefix}_title.txt", post["title"])
        save_text(out_dir, f"{prefix}.html", full_html)
        save_text(out_dir, f"{prefix}_tags.txt", ", ".join(post["tags"]))
        print(f"  -> 저장 완료: {out_dir}/{prefix}.html (이미지 {len(image_urls)}장, 쇼핑링크 {'O' if shopping_html else 'X'})")

        if publish:
            try:
                result = post_to_naver_blog(post["title"], full_html, post["tags"])
                print(f"  -> 네이버 블로그 업로드 완료: {result}")
            except Exception as e:
                print(f"  ! 네이버 블로그 업로드 실패: {e}")

        if i < count and interval_min > 0:
            print(f"  ... 다음 글까지 {interval_min}분 대기 (연속 도배 방지)")
            time.sleep(interval_min * 60)

    print(f"\n완료! 총 {count}개 글을 '{out_dir}' 폴더에 저장했습니다.")


def main():
    parser = argparse.ArgumentParser(description="블로그/인스타/영상 콘텐츠 자동 생성")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="오늘의 콘텐츠 생성 (블로그+인스타+영상)")
    run_parser.add_argument("--keyword", type=str, default=None, help="키워드 직접 지정 (생략 시 오늘의 트렌드 자동 사용)")
    run_parser.add_argument("--publish-blog", action="store_true", help="생성 후 네이버 블로그에 실제로 업로드")

    blog_parser = subparsers.add_parser("blog", help="하루치 블로그 글만 대량 생성 (이미지+쇼핑링크 포함)")
    blog_parser.add_argument("--count", type=int, default=config.POSTS_PER_DAY, help="발행할 글 개수 (기본 15개)")
    blog_parser.add_argument("--publish", action="store_true", help="생성 후 네이버 블로그에 실제로 업로드")
    blog_parser.add_argument(
        "--interval-min", type=float, default=0, help="글 사이 대기 시간(분). 도배성 업로드 방지를 위해 권장 (예: 20)"
    )

    args = parser.parse_args()

    if args.command == "run":
        run(args.keyword, args.publish_blog)
    elif args.command == "blog":
        run_blog_batch(args.count, args.publish, args.interval_min)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
