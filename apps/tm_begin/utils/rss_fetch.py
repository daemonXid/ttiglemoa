# apps/tm_begin/utils/rss_fetch.py
import time, html, re
import feedparser, requests
from bs4 import BeautifulSoup
from typing import Iterable, Optional

TAG_RE = re.compile(r"<[^>]+>")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

def clean_text(s: str | None) -> str:
    if not s: return ""
    s = TAG_RE.sub("", html.unescape(s)).strip()
    return re.sub(r"\s+", " ", s)

def _extract_summary(e) -> str:
    # summary → description → summary_detail.value → content[0].value
    candidates = [
        e.get("summary"),
        e.get("description"),
        getattr(e, "summary_detail", {}).get("value") if hasattr(e, "summary_detail") else None,
    ]
    content = getattr(e, "content", None)
    if content and isinstance(content, list):
        for c in content:
            v = c.get("value")
            if v:
                candidates.append(v)
                break

    for c in candidates:
        if c:
            txt = clean_text(c)
            if txt:
                return txt
    return ""  # 비어있으면 템플릿에서 자동으로 숨김

def _first_image_from_feed_entry(e) -> Optional[str]:
    mc = getattr(e, "media_content", None)
    if mc and isinstance(mc, list):
        for m in mc:
            url = m.get("url")
            if url: return url
    for l in (e.get("links", []) or getattr(e, "links", []) or []):
        if l.get("rel") == "enclosure" and "image" in (l.get("type") or ""):
            return l.get("href")
    return None

def _get_og_image(url: str, timeout: int = 6) -> Optional[str]:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
        if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type",""):
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.select_one('meta[property="og:image"], meta[name="og:image"]')
        if tag:
            c = tag.get("content")
            if c and c.startswith("http"):
                return c
    except Exception:
        return None
    return None

def fetch_rss_many(urls: Iterable[str], limit_per_feed: int = 100, try_scrape_og_image: bool = True, scrape_limit: int = 6) -> list[dict]:
    items, tried = [], 0
    for url in urls:
        d = feedparser.parse(url, request_headers={"User-Agent": UA})
        for e in d.entries[:limit_per_feed]:
            ts = None
            if getattr(e, "published_parsed", None):
                ts = time.mktime(e.published_parsed)
            elif getattr(e, "updated_parsed", None):
                ts = time.mktime(e.updated_parsed)

            link = e.get("link")
            img = _first_image_from_feed_entry(e)
            if not img and try_scrape_og_image and link and tried < scrape_limit:
                og = _get_og_image(link)
                if og: img = og
                tried += 1

            items.append({
                "title": clean_text(e.get("title")),
                "link": link,
                "summary": _extract_summary(e),   # ← 강화
                "published": e.get("published") or e.get("updated") or "",
                "ts": ts,
                "source": "Investing.com",
                "img": img,
            })
    items.sort(key=lambda x: (x["ts"] is None, x["ts"], x["published"]), reverse=True)
    return items
