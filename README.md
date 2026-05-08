# final-project

## 組員
- 傅香瑋
- 簡貝珊

# Smart Wardrobe & Style Persona

## 專題主題
智慧極簡衣櫥與穿搭分析鏡

## 專題介紹
本專題結合 Flask、資料庫、網路爬蟲與 Jetson Nano 視覺辨識技術，
建立一個智慧穿搭分析系統。

系統可以：
- 分析使用者穿搭風格
- 提供穿搭建議
- 顯示流行服飾資訊
- 整合資料庫與網頁介面

---

## 使用技術
- Flask
- SQLite
- Python
- BeautifulSoup
- Jetson Nano

---

# 啟動方式

## 建立虛擬環境
python3 -m venv .venv

## 啟動虛擬環境
source .venv/bin/activate

## 安裝 Flask
pip install flask flask_sqlalchemy

## 啟動網站
python3 app.py