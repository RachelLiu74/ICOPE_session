# ICOPE 暖身問答 v3

課堂 PPT 報告前的 warm-up 互動問答系統。學生用手機或電腦作答，老師可即時查看統計與下載結果。

## 功能特色

- **學生端**：姓名（必填）＋ 組別下拉選單（必填，共 8 組，含「其他」）＋ 代號（選填）→ 逐題作答，**每題一個頁籤**，可用頁籤或上一題／下一題按鈕切換，介面支援手機與電腦瀏覽器。
- **老師端**：登入密碼 `分機號碼`，可查看人數、平均分數、平均作答時間、每題作答分布，並下載 CSV。
- **題目結構（共 9 題）**：
  - Q1–5：想法投票（單選，無標準答案，僅統計選項分布）
  - Q6–7：單選題（有標準答案，計分）
  - Q8–9：複選題（有標準答案，需完全選對才算分）

## 專案結構

```
app.py               # Flask 後端（API、資料庫、CSV 匯出）
questions.py          # 題庫與組別名單
templates/index.html  # 前端頁面（單頁應用）
static/app.js          # 前端邏輯
static/style.css       # 前端樣式
requirements.txt       # Python 相依套件
Procfile / render.yaml # 雲端部署設定（Render）
```

## 本機執行

需求：Python 3.9+（開發時使用 conda 環境 `FY115_igmosaic`）。

```powershell
pip install -r requirements.txt
python app.py
```

伺服器預設監聽 `PORT` 環境變數指定的埠號，若未設定則使用 `5057`。啟動後於同網段裝置開啟：

```
http://<本機IP>:5057/
```

資料儲存在本機 SQLite 檔案 `icope_qa.db`（已加入 `.gitignore`，不會上傳）。

## 雲端部署（Render / Railway 等）

專案已附上 `Procfile` 與 `render.yaml`，可直接以 Python/gunicorn 服務部署：

```
web: gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT
```

**注意**：免費方案通常使用暫時性檔案系統，服務重啟或閒置休眠後 SQLite 資料庫內容可能會遺失，僅適合單堂課程的臨時使用，如需長期保存資料建議改用外部資料庫服務。

## 用 GitHub Codespaces 快速對外測試

專案已附上 `.devcontainer/devcontainer.json`，可直接在 GitHub 上開一個雲端開發環境測試，不需要另外註冊部署平台帳號：

1. 到 GitHub 上的 repo 頁面，點選綠色 **Code** 按鈕 → **Codespaces** 分頁 → **Create codespace on main**。
2. 等待環境建立完成（會自動執行 `pip install -r requirements.txt`），接著會自動在背景啟動 `python app.py`（監聽埠 `5057`）。
3. Codespace 會自動偵測到埠 `5057` 並跳出預覽視窗；下方 **PORTS** 分頁可以看到該埠已設定為 **Public**，複製該網址即可分享給任何人在瀏覽器開啟（手機／電腦皆可）。
4. 若要重新啟動伺服器（例如改了程式碼），在 Codespace 的終端機執行：
   ```bash
   pkill -f "python app.py"; python app.py
   ```

**注意**：Codespaces 免費額度有限（依 GitHub 帳號方案而定），且每次重新建立 Codespace 網址都會改變，資料庫也只存在該 Codespace 內、刪除後就會消失，僅適合臨時測試，正式對外長期使用建議改用 Render／Railway。

## 用 GitHub Pages 部署靜態版（無登入/無統計，僅簡報用）

GitHub Pages 只能放靜態網頁，無法執行 Flask 後端，因此這裡部署的是**不需要伺服器**的獨立版本 [ICOPE_warmup_10Q.html](ICOPE_warmup_10Q.html)（已複製一份到 `docs/index.html`），適合單純簡報 / 課堂投影片使用，沒有學生登入、老師統計、CSV 下載等功能。

啟用步驟（只需設定一次）：

1. 到 GitHub 上的 repo 頁面 → **Settings** → 左側選單 **Pages**。
2. **Build and deployment** → **Source** 選擇 **Deploy from a branch**。
3. **Branch** 選擇 `main`，資料夾選擇 **/docs**，按 **Save**。
4. 等待約 1 分鐘，頁面會顯示發佈完成的網址，格式類似：
   ```
   https://rachelliu74.github.io/ICOPE_session/
   ```
5. 之後若要更新內容，只要修改 `docs/index.html` 並 push 到 `main`，GitHub Pages 會自動重新部署。

若要對外提供完整互動（學生登入、計分、老師統計），請改用上面的 Render 部署或 GitHub Codespaces。

## 老師登入密碼

預設密碼為 `分機號碼`，正式對外使用前請至 [app.py](app.py) 修改 `TEACHER_PASSWORD`。
