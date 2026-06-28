# 智慧極簡衣櫥 - Smart Minimalist Wardrobe

## 組員
- 傅香瑋
- 簡貝珊

## 專題簡介

每個人的身形都不同，但市面上的穿搭建議往往是通用的。我們設計一個系統，用**數學模型**自動分類使用者體型，給出**客製化穿搭建議**。

### 核心功能
- 衣櫥管理：新增、查看、刪除衣服
- **體型分析**：輸入三圍（胸、腰、臀）自動分類
  - 沙漏型、梨型、蘋果型、倒三角型、矩形型
- 穿搭推薦：隨機組合衣服推薦

### 技術棧
- 前端：Flask + HTML/CSS
- 後端：Python Flask + SQLAlchemy ORM
- 資料庫：PostgreSQL (Render)
- 爬蟲：Python requests
- 部署：Render + Gunicorn

## 線上訪問
🌐 **https://final-project-dmxc.onrender.com**

## 本地運行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

訪問 `http://localhost:5000`

## 展示影片
📹 [期末專題展示影片](https://drive.google.com/drive/folders/12mCtothlZEPGZyyo97sqAte9hVs1kal9?usp=drive_link)

## 小組分工
- **傅香瑋**：前端設計、爬蟲開發、部署配置
- **簡貝珊**：體型分類演算法、後端路由、資料庫設計

## GitHub
https://github.com/Bella1015-tech/final-project
