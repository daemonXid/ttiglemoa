# apps/tm_begin/views.py
from django.shortcuts import render
from django.utils import timezone
from .utils.rss_fetch import fetch_rss_many
from django.core.paginator import Paginator

# ---- RSS 설정 ----
INVESTING_FEEDS = [
    "https://kr.investing.com/rss/news.rss",
    # 필요시 카테고리 추가:
    # "https://www.investing.com/rss/news_14.rss", # 경제 지표 뉴스
    # "https://www.investing.com/rss/news_301.rss",# 외환 뉴스
]

# ---- 초간단 메모리 캐시 ----
_CACHE = {"items": [], "at": None}
_CACHE_TTL = 60 * 10  # 10분





def _get_investing_news(limit=200):  # 페이지네이션용 여유 있게 가져오기
    now = timezone.now()
    must_refresh = (
        _CACHE["at"] is None
        or (now - _CACHE["at"]).total_seconds() > _CACHE_TTL
    )
    if must_refresh:
        items = fetch_rss_many(
            INVESTING_FEEDS,
            limit_per_feed=120,     # 넉넉히
            try_scrape_og_image=True,
            scrape_limit=8,
        )
        _CACHE["items"] = items
        _CACHE["at"] = now
    return _CACHE["items"][:limit], _CACHE["at"]

def index(request):
    news_list, updated_at = _get_investing_news(limit=20)  # 인덱스는 1페이지 느낌으로 13개만
    return render(request, "common/index.html", {
        "news_list": news_list,
        "updated_at": updated_at,
        "count": len(news_list),
    })

def investing_news(request):
    # 데이터 로드(여유 있게)
    items, updated_at = _get_investing_news(limit=200)
    
    # Paginator를 사용하여 페이지네이션 처리
    paginator = Paginator(items, 9)  # 한 페이지에 9개씩
    selected_page_num = request.GET.get("page")
    page_obj = paginator.get_page(selected_page_num)

    hero_item = page_obj.object_list[0] if page_obj.object_list else None
    grid_items = page_obj.object_list[1:] if len(page_obj.object_list) > 1 else []

    # 페이지 번호(현재±2)
    page_group = 2
    start_num = max(1, page_obj.number - page_group)
    end_num   = min(paginator.num_pages, page_obj.number + page_group)
    page_numbers = list(range(start_num, end_num + 1))

    ctx = {
        "updated_at": updated_at,
        "count": len(page_obj.object_list),       # 이 페이지에서 보여주는 개수(최대 13)
        "total": paginator.count,                 # 전체 개수
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        "page_numbers": page_numbers,
        "has_prev": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "prev_page": page_obj.previous_page_number() if page_obj.has_previous() else 1,
        "next_page": page_obj.next_page_number() if page_obj.has_next() else paginator.num_pages,
        "hero_item": hero_item,
        "grid_items": grid_items,
    }
    return render(request, "tm_begin/each_pages/stock_news.html", ctx)



def about(request):
    return render(request, "tm_begin/each_pages/about.html")



