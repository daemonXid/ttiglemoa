// ==========================
// 📌 Stock News Section
// ==========================
document.addEventListener("DOMContentLoaded", function() {
  const root = document.getElementById("stock-news-root");
  const newsContent = document.getElementById("news-content-main");
  const newsMeta = document.getElementById("news-meta-main");
  const loadingSpinner = document.getElementById("loading-spinner-main");
  if (!root || !newsContent || !newsMeta || !loadingSpinner) return;

  // 1) HTML data-attr 우선 사용, 없으면 하드코딩 백업 경로 사용
  //    (하드코딩 경로는 실제 urls.py와 다를 수 있으니 꼭 data-*로 심는 걸 권장)
  const endpoint =
    root.getAttribute("data-news-endpoint") || "/tm_begin/index_json/";

  // 타임아웃/취소를 위한 AbortController (네트워크가 멈출 때 대비)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s

  async function fetchAndRenderNews() {
    loadingSpinner.style.display = "flex";

    try {
      const resp = await fetch(endpoint, {
        method: "GET",
        headers: { "Accept": "application/json" },
        signal: controller.signal,
        // credentials: "same-origin", // (로그인이 필요한 엔드포인트라면 활성화)
      });

      // (A) 네트워크/상태코드 문제 추적
      if (!resp.ok) {
        const text = await resp.text();
        console.error("❌ News fetch failed:", resp.status, resp.statusText, text);
        newsContent.innerHTML = `<p>뉴스를 불러오는 데 실패했습니다. (HTTP ${resp.status})</p>`;
        return;
      }

      // (B) 로그인 리다이렉트/HTML 응답 탐지 (종종 200인데 HTML일 수 있음)
      const contentType = resp.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const text = await resp.text();
        console.error("❌ Not JSON (maybe login redirect or template?):", text.slice(0, 400));
        newsContent.innerHTML = `<p>뉴스를 불러오는 데 실패했습니다. (JSON 아님)</p>`;
        return;
      }

      const data = await resp.json();

      newsContent.innerHTML = "";
      newsMeta.innerHTML = "";

      if (data.updated_at) {
        newsMeta.textContent = `업데이트: ${data.updated_at} (${data.count}건)`;
      }

      if (Array.isArray(data.news_list) && data.news_list.length > 0) {
        newsContent.innerHTML += renderHeroItem(data.news_list[0]);

        const gridContainer = document.createElement("div");
        gridContainer.className = "inv-row";
        data.news_list.slice(1, 5).forEach(item => {
          gridContainer.innerHTML += renderGridItem(item);
        });
        newsContent.appendChild(gridContainer);
      } else {
        newsContent.innerHTML = "<p>표시할 뉴스가 없어요. 잠시 후 다시 시도해 주세요.</p>";
      }
    } catch (err) {
      if (err.name === "AbortError") {
        console.error("⏱️ Fetch aborted (timeout).");
        newsContent.innerHTML = "<p>요청이 지연되어 중단되었습니다. 다시 시도해 주세요.</p>";
      } else {
        console.error("❌ Error fetching news:", err);
        newsContent.innerHTML = "<p>뉴스를 불러오는 데 실패했습니다.</p>";
      }
    } finally {
      clearTimeout(timeoutId);
      loadingSpinner.style.display = "none";
    }
  }

  function renderHeroItem(item) {
    const image = item.img
      ? `<img src="${item.img}" alt="${escapeHtml(item.title)}">`
      : '<div class="no-image"><span>📈</span></div>';
    const summary = item.summary
      ? `<p class="inv-desc inv-line-5">${escapeHtml(item.summary)}</p>`
      : "";
    return `
      <div class="inv-hero">
        <div class="inv-hero-img">
          <a href="${item.link}" target="_blank" rel="noopener">
            ${image}
          </a>
        </div>
        <div class="inv-hero-content">
          <a href="${item.link}" target="_blank" rel="noopener" class="inv-title-lg inv-hero-title">
            ${escapeHtml(item.title)}
          </a>
          ${summary}
          <div class="inv-meta">
            <time>${escapeHtml(item.published || "")}</time>
            <span>${escapeHtml(item.source || "")}</span>
          </div>
        </div>
      </div>
    `;
  }

  function renderGridItem(item) {
    const image = item.img
      ? `<img src="${item.img}" alt="${escapeHtml(item.title)}">`
      : '<div class="no-image-small"><span>📰</span></div>';
    return `
      <div class="inv-card">
        <a href="${item.link}" target="_blank" rel="noopener" class="inv-thumb">
          ${image}
        </a>
        <a href="${item.link}" target="_blank" rel="noopener" class="inv-title inv-line-2">
          ${escapeHtml(item.title)}
        </a>
        <div class="inv-meta">
          <time>${escapeHtml(item.published || "")}</time>
        </div>
      </div>
    `;
  }

  // XSS 방지용 간단 이스케이프
  function escapeHtml(str) {
    if (typeof str !== "string") return "";
    return str
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  fetchAndRenderNews();
});
