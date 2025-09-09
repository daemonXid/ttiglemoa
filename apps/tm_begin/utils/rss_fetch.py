# apps/tm_begin/utils/rss_fetch.py
# --- 리팩토링 버전 (안정성/정확도/커버리지 개선) ---

import re, html, time, calendar
from typing import Iterable, Optional
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

# HTML 태그 제거용 정규식
TAG_RE = re.compile(r"<[^>]+>")

# User-Agent (일부 서버는 기본 UA 차단)
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {"User-Agent": UA}


def clean_text(s: str | None) -> str:
    """HTML 태그/엔티티 제거 + 공백 정리."""
    if not s:
        return ""
    s = TAG_RE.sub("", html.unescape(s)).strip()
    return re.sub(r"\s+", " ", s)


def _extract_summary(e) -> str:
    """
    RSS 엔트리에서 요약 텍스트를 우선순위대로 추출.
    summary → description → summary_detail.value → content[0].value
    """
    candidates: list[Optional[str]] = [
        e.get("summary"),
        e.get("description"),
    ]

    # summary_detail.value (객체/딕셔너리 모두 안전 처리)
    sd = getattr(e, "summary_detail", None)
    if sd:
        val = getattr(sd, "value", None)
        if val is None and isinstance(sd, dict):
            val = sd.get("value")
        candidates.append(val)

    # content[0].value
    content = getattr(e, "content", None)
    if content and isinstance(content, list):
        for c in content:
            v = c.get("value") if isinstance(c, dict) else None
            if v:
                candidates.append(v)
                break

    for c in candidates:
        if c:
            txt = clean_text(c)
            if txt:
                return txt
    return ""


def _first_image_from_feed_entry(e) -> Optional[str]:
    """
    RSS 엔트리 메타(media_content, media_thumbnail, enclosure 링크 등)에서 이미지 URL을 추출.
    """
    # 1) <media:content url="...">
    mc = getattr(e, "media_content", None)
    if mc and isinstance(mc, list):
        for m in mc:
            url = m.get("url")
            if url:
                return url

    # 2) <media:thumbnail url="...">
    thumbs = getattr(e, "media_thumbnail", None)
    if thumbs and isinstance(thumbs, list):
        for t in thumbs:
            url = t.get("url")
            if url:
                return url

    # 3) enclosure 링크(type에 image 포함)
    links = e.get("links", None) or getattr(e, "links", None) or []
    for l in links:
        if l.get("rel") == "enclosure" and "image" in (l.get("type") or ""):
            href = l.get("href")
            if href:
                return href

    return None


def _get_og_image(url: str, session: requests.Session, timeout: int = 6) -> Optional[str]:
    """
    본문 페이지에서 og:image/twitter:image를 추출.
    상대경로는 원문 URL 기준으로 절대경로로 보정.
    """
    try:
        r = session.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type", ""):
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        # 우선 og:image, 없으면 twitter:image 도 시도
        tag = soup.select_one('meta[property="og:image"], meta[name="og:image"]') or \
              soup.select_one('meta[name="twitter:image"], meta[property="twitter:image"]')
        if not tag:
            return None

        content = tag.get("content")
        if not content:
            return None

        # 상대경로 → 절대경로
        return urljoin(url, content)

    except Exception:
        return None


def _to_epoch_utc(entry) -> Optional[int]:
    """
    published_parsed / updated_parsed(struct_time, UTC 가정)를 epoch(초)로 변환.
    calendar.timegm 사용(UTC 기준, DST 안전).
    """
    st = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not st:
        return None
    try:
        return calendar.timegm(st)  # UTC struct_time → epoch seconds
    except Exception:
        return None


def fetch_rss_many(
    urls: Iterable[str],
    limit_per_feed: int = 100,
    try_scrape_og_image: bool = True,
    scrape_limit: int = 6,
) -> list[dict]:
    """
    여러 RSS 피드를 읽어 통합 리스트를 만들고, 최신 순으로 정렬해 반환.
    - urls: 피드 URL 모음
    - limit_per_feed: 피드당 최대 엔트리 수
    - try_scrape_og_image: 이미지가 없을 때 본문 페이지에서 og:image 시도 여부
    - scrape_limit: og:image 스크랩 시도 상한(과도한 네트워크 요청 방지)
    """
    items: list[dict] = []
    tried = 0

    with requests.Session() as session:
        for url in urls:
            # feedparser 요청 시 UA 지정
            d = feedparser.parse(url, request_headers=HEADERS)

            # 파싱 에러(bozo) 있으면 넘어가되, 필요시 로깅 고려
            # if getattr(d, "bozo", 0):
            #     print("RSS parse warning:", url, getattr(d, "bozo_exception", None))

            for e in d.entries[:limit_per_feed]:
                ts = _to_epoch_utc(e)
                link = e.get("link")

                # 피드 자체에서 이미지 탐색
                img = _first_image_from_feed_entry(e)

                # 이미지가 없으면 og:image 시도(상한 제한)
                if not img and try_scrape_og_image and link and tried < scrape_limit:
                    og = _get_og_image(link, session=session)
                    if og:
                        img = og
                    tried += 1

                items.append(
                    {
                        "title": clean_text(e.get("title")),
                        "link": link,
                        "summary": _extract_summary(e),
                        "published": e.get("published") or e.get("updated") or "",
                        "ts": ts,  # 정렬용 epoch(UTC)
                        "source": "Investing.com",
                        "img": img,
                    }
                )

    # 최신순 정렬:
    # 1) ts가 있는 항목이 먼저
    # 2) ts가 큰(최신) 순으로
    items.sort(key=lambda x: (x["ts"] is None, -(x["ts"] or 0)))

    return items
