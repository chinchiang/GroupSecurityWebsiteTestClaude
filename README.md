# 資安防護網設計手冊網站（GSMD-RPT-2026-0830-01）

「跨國 ODM/OEM 製造業集團 IT 資安防護網設計手冊」的靜態網站骨架。
純 HTML/CSS/JS，無建置流程、無相依套件，clone 下來直接用瀏覽器開啟 `index.html` 即可。

## 網站結構

| 頁面 | 內容 |
|---|---|
| `index.html` | 首頁：執行摘要、五項關鍵發現、三年投資排序、董事會三問、閱讀路徑 |
| `methodology.html` | 方法論：四級證據分級、三條查證紀律、十六項 2026 時效性警示 |
| `part-1.html` | 第 I 部（第 1–6 章）：背景與威脅情勢 |
| `part-2.html` | 第 II 部（第 7–10 章）：框架選擇、設計十原則、總體架構 |
| `part-3.html` | 第 III 部（第 11–23 章）：L0–L9 分層設計與三個橫切面 |
| `part-4.html` | 第 IV 部（第 24–30 章）：組織、預算、成熟度與治理 |
| `appendix.html` | 附錄 A–H：總表、自評問卷、Claude Code + GitHub Prompt 套件 |

共用資產在 `assets/css/main.css`（含深色模式支援）與 `assets/js/main.js`。

內文回填進度：**全部頁面已完成回填**——`index.html`、`methodology.html`、
`part-1.html`（第 1–6 章）、`part-2.html`（第 7–10 章）、`part-3.html`（第 11–23 章）、
`part-4.html`（第 24–30 章）、`appendix.html`（附錄 A–H）。
完整內容來源為 `docs/GSMDRPT2026083001.md`。

`part-1.html` 為內文頁的**版型範本**：頁內目錄 `.toc`、章節標題 `.chapter-head`、
內文容器 `.section.prose`、來源註記 `.src-note`、推論方塊 `.notice.accent`（青）、
警示方塊 `.notice`（金）、章末產出清單 `.deliverables`、回目錄 `.to-top`。
其餘各部回填時直接沿用這組 class，不要另寫 inline style。

## 本機預覽

```bash
python3 -m http.server 8000
# 開啟 http://localhost:8000
```

## 部署（GitHub Pages）

Repo Settings → Pages → Build and deployment → Source 選 **GitHub Actions**。
`.github/workflows/deploy-pages.yml` 會在 push 到 `main` 時組裝站台並部署，
且刻意排除 `docs/`（手冊全文）、`README.md` 與 `.github/`。

> **不要**改選「Deploy from a branch」：那會把整個分支根目錄（含 `docs/` 手冊全文）
> 原樣公開到 Pages。

> **注意**：依手冊附錄 F 的安全前提，若後續在本 repo 填入集團的控制項現況、
> 評估結果或缺口資料，repo 應設為 **private**——這些內容本身就是高價值的攻擊情報。

## 內容維護原則（摘自手冊）

- 每一個事實性陳述都必須標註證據等級：【已證實】／【廠商主張】／【第三方評論】／【尚未證實】
- 無來源不列入；口徑一致才可比較；方法一致才可畫趨勢
- 標準引用必須含版本與日期（查證基準日 2026-08-30）
