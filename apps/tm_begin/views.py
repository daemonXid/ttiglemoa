# apps/tm_begin/views.py
from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .utils.rss_fetch import fetch_rss_many
from apps.tm_assets.models import DepositSaving, StockHolding, BondHolding

# ---- RSS 설정 ----
INVESTING_FEEDS = [
    "https://kr.investing.com/rss/news.rss",
    "https://kr.investing.com/rss/news_14.rss",  # 경제 지표
    "https://kr.investing.com/rss/news_301.rss", # 외환
]

# ---- 초간단 메모리 캐시 ----
_CACHE = {"items": [], "at": None}
_CACHE_TTL = 60 * 10  # 10분

def _get_investing_news(limit=200):
    """Investing.com 뉴스: 캐시 10분. 반환: (items[:limit], updated_at)"""
    now = timezone.now()
    must_refresh = (_CACHE["at"] is None) or ((now - _CACHE["at"]).total_seconds() > _CACHE_TTL)
    if must_refresh:
        items = fetch_rss_many(
            INVESTING_FEEDS,
            limit_per_feed=120,
            try_scrape_og_image=True,
            scrape_limit=8,
        )
        _CACHE["items"] = items
        _CACHE["at"] = now
    return _CACHE["items"][:limit], _CACHE["at"]

def index(request):
    # 홈: 가볍게 20개만
    news_list, updated_at = _get_investing_news(limit=20)
    return render(request, "common/index.html", {
        "news_list": news_list,
        "updated_at": updated_at,
        "count": len(news_list),
    })

def investing_news(request):
    # 목록: 페이지당 9개 (히어로 1 + 카드 그리드)
    items, updated_at = _get_investing_news(limit=200)
    paginator = Paginator(items, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    hero_item = page_obj.object_list[0] if page_obj.object_list else None
    grid_items = page_obj.object_list[1:] if len(page_obj.object_list) > 1 else []

    # 페이지 번호(현재±2)
    page_group = 2
    start_num = max(1, page_obj.number - page_group)
    end_num   = min(paginator.num_pages, page_obj.number + page_group)
    page_numbers = list(range(start_num, end_num + 1))

    ctx = {
        "updated_at": updated_at,
        "count": len(page_obj.object_list),
        "total": paginator.count,
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
    return render(request, "tm_begin/stock_news.html", ctx)

def search(request):
    query = request.GET.get('q')
    news_results = []
    portfolio_results = {
        'deposit_savings': [],
        'stock_holdings': [],
        'bond_holdings': [],
    }

    if query:
        # 뉴스 검색(제목/요약)
        all_news, _ = _get_investing_news(limit=1000)
        q = query.lower()
        news_results = [
            item for item in all_news
            if q in item.get('title', '').lower()
            or q in item.get('summary', '').lower()
        ]

        # 포트폴리오 검색
        portfolio_results['deposit_savings'] = DepositSaving.objects.filter(
            Q(bank_name__icontains=query) | Q(product_name__icontains=query)
        )
        portfolio_results['stock_holdings'] = StockHolding.objects.filter(
            Q(ticker__icontains=query) | Q(name__icontains=query)
        )
        portfolio_results['bond_holdings'] = BondHolding.objects.filter(
            Q(name__icontains=query) | Q(issuer__icontains=query)
        )

    context = {
        'query': query,
        'news_results': news_results,
        'portfolio_results': portfolio_results,
    }
    return render(request, 'tm_begin/search_results.html', context)

def about(request):
    return render(request, "tm_begin/about.html")
