# 資安防護網設計手冊網站（GSMD-RPT-2026-0830-01）

「跨國 ODM/OEM 製造業集團 IT 資安防護網設計手冊」的靜態網站版本。
純 HTML/CSS/JS，無建置流程、無相依套件，clone 下來直接用瀏覽器開啟 `index.html` 即可。

## 網站結構

| 頁面 | 內容 |
|---|---|
| `index.html` | 首頁（§0.1、§0.5）：執行摘要、五項關鍵發現、三年投資排序、董事會三問、閱讀路徑、文件資訊與版本說明 |
| `methodology.html` | 方法論（§0.2–§0.4）：四級證據分級、三條查證紀律、名詞與範圍界定、十六項 2026 時效性警示 |
| `part-1.html` | 第 I 部（第 1–6 章）：背景與威脅情勢 |
| `part-2.html` | 第 II 部（第 7–10 章）：框架選擇、設計十原則、總體架構 |
| `part-3.html` | 第 III 部（第 11–23 章）：L0–L9 分層設計與三個橫切面 |
| `part-4.html` | 第 IV 部（第 24–30 章）：組織、預算、成熟度與治理 |
| `appendix.html` | 附錄 A–H：總表、自評問卷、Claude Code + GitHub Prompt 套件 |

共用資產在 `assets/css/main.css`（含深色模式支援）與 `assets/js/main.js`。

內文回填進度：**前言 §0.1–§0.5、第 1–30 章、附錄 A–H 均已依原文回填**。
完整內容來源為 `docs/GSMDRPT2026083001.md`；網站與原文不一致時，以原文為準並回頭修正網站。

`part-1.html` 為內文頁的**版型範本**：頁內目錄 `.toc`、章節標題 `.chapter-head`、
內文容器 `.section.prose`、來源註記 `.src-note`、推論方塊 `.notice.accent`（青）、
警示方塊 `.notice`（金）、章末產出清單 `.deliverables`、回目錄 `.to-top`。
其餘各部回填時直接沿用這組 class，不要另寫 inline style。

小節錨點：編號小節標題一律帶 `id="s{章}-{節}"`（如 `s5-2`、`s5-2-1`、`sF-2`），
前言為 `s0-2`–`s0-4`（`methodology.html`）與 `s0-5`（`index.html`）。
內文的「§x.y」交互參照應直接連到該小節錨點，而非只連到章（`#chN`）；
只提到「第 N 章」時則連到該章錨點（如 `part-3.html#ch17`）。

證據標籤一律寫成 `<span class="ev ev-verified">已證實</span>`（不加【】括號；
另有 `ev-vendor`、`ev-third`、`ev-unverified`）。標籤文字須以該 class 對應的四級名稱開頭，
補充說明接在後面（如「第三方評論・完整 Reprint」）。「公知」「本手冊查證結論」不是四級之一，以純文字呈現。
查證基準日（2026-08-30）之後才會發生或可能變動的狀態，須註明「截至 2026-08-30」。
各內文頁頂端的 `.asof-banner` 提示全站內容以查證基準日為準；改版重新查證後須一併更新日期。

## 本機預覽

```bash
python3 -m http.server 8000
# 開啟 http://localhost:8000
```

## 自動檢查

`.github/scripts/check_site.py`（僅用 Python 標準函式庫）檢查：HTML 標籤結構、重複 id、
站內連結與錨點、本站 CSS／JS／圖示資源存在、證據標籤 class 與文字相符且不加【】、禁用 inline style／`<style>`／inline `<script>`、
每頁須有 `noindex` 與 meta description、HTML 用到的 class 須在 `main.css` 定義、內文字元須在字型子集內。

```bash
python3 .github/scripts/check_site.py              # 站內檢查
python3 .github/scripts/check_site.py --external   # 另查外部連結（僅 404/410 視為失效）
```

`.github/workflows/check-site.yml` 在 PR 與 push 到 `main` 時跑站內檢查，每週一另跑外部連結檢查；
`deploy-pages.yml` 部署前也會先跑站內檢查，未通過就不部署。

各頁設有 Content-Security-Policy（只允許本站資源），因此**不可使用 inline script／style**。

字型（Noto Sans TC／Noto Serif TC，SIL OFL 授權，見 `assets/fonts/OFL.txt`）由本站提供、不連 Google Fonts
（中國大陸無法存取，也避免把瀏覽紀錄交給第三方），並子集化為網站實際用到的字元（兩檔合計約 1 MB）。
內文新增字元後，`check_site.py` 會回報「字型子集缺字」，此時依 `.github/scripts/build_fonts.py`
開頭的說明重建字型（需 fonttools，僅本機執行）。
`404.html` 以 `<base href="/GroupSecurityWebsiteTestClaude/">` 固定資源路徑；repo 改名時須一併修改。

## 部署（GitHub Pages）

Repo Settings → Pages → Build and deployment → Source 選 **GitHub Actions**。
`.github/workflows/deploy-pages.yml` 會在 push 到 `main` 時組裝站台並部署，
且刻意排除 `docs/`（手冊全文）、`README.md` 與 `.github/`。

> **不要**改選「Deploy from a branch」：那會把整個分支根目錄（含 `docs/` 手冊全文）
> 原樣公開到 Pages。

部署失敗時，先看該次 run 的 annotation（log 過期後仍保留，可用
`gh api repos/{owner}/{repo}/check-runs/{id}/annotations` 查），過去遇過的原因：

| 現象 | 原因 | 處理 |
|---|---|---|
| job 沒有任何 step 就失敗 | 帳號付款失敗或 Actions 花費上限不足，job 未啟動 | 到 Settings → Billing & plans 處理後重跑 |
| `Get Pages site failed: Not Found` | Pages 來源尚未設為 GitHub Actions | 依上方設定 Source |
| 部署步驟被拒 | `github-pages` 環境只允許 `main` 部署 | 從 `main` 部署，勿從其他分支觸發 |

Action 版本由 `.github/dependabot.yml` 每月自動提 PR 更新（仍以 commit SHA 釘選）。

> **密級**：本版為**公開 / Public（通用參考版）**，不含任何集團實際控制項現況、評估結果或缺口資料。
> 網站各頁均設 `<meta name="robots" content="noindex, nofollow">`，避免被搜尋引擎收錄；
> 這只防搜尋曝光、不是存取控制——網址與公開 repo 內容仍可被任何人讀取。

> **注意**：依手冊附錄 F 的安全前提，若後續在本 repo 填入集團的控制項現況、
> 評估結果或缺口資料，repo 應設為 **private**——這些內容本身就是高價值的攻擊情報。

## 內容維護原則（摘自手冊）

- 每一個事實性陳述都必須標註證據等級：【已證實】／【廠商主張】／【第三方評論】／【尚未證實】
- 無來源不列入；口徑一致才可比較；方法一致才可畫趨勢
- 標準引用必須含版本與日期（查證基準日 2026-08-30）
