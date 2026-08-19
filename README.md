# ICOPE 暖身問答 v3

課堂 PPT 報告前的 warm-up 互動問答系統。學生用手機或電腦作答，老師可即時查看統計與下載結果。

## 功能特色

- **學生端**：姓名（必填）＋ 組別下拉選單（必填，共 8 組，含「其他」）＋ 代號（選填）→ 逐題作答，**每題一個頁籤**，可用頁籤或上一題／下一題按鈕切換，介面支援手機與電腦瀏覽器。
- **老師端**：登入密碼 `17383`，可查看人數、平均分數、平均作答時間、每題作答分布，並下載 CSV。
- **題目結構（共 10 題）**：
  - Q1–5：想法投票（單選，無標準答案，僅統計選項分布）
  - Q6–8：單選題（有標準答案，計分）
  - Q9–10：複選題（有標準答案，需完全選對才算分）

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

## 老師登入密碼

預設密碼為 `17383`，正式對外使用前請至 [app.py](app.py) 修改 `TEACHER_PASSWORD`。
