import random
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ==========================================
# 1. 資料庫設定 (SQLite)
# ==========================================
import os
from dotenv import load_dotenv
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wardrobe.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 建立資料庫模型 - 衣服
class Clothing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=True)  
    image_url = db.Column(db.String(300), nullable=True) 

# 修改 app.py 裡的初始化區塊
with app.app_context():
    db.create_all()
    # if not Clothing.query.first():
    #     sample_clothes = [
    #         # 這裡幫初始衣服補上網址
    #         Clothing(name="日系極簡藍 T 恤", category="上衣", color="藍色", image_url="https://www.uniqlo.com/tw/hmall/test/u0000000052833/main/first/561/1.jpg"),
    #         Clothing(name="重磅極致黑 T 恤", category="上衣", color="黑色", image_url="https://www.uniqlo.com/tw/hmall/test/u0000000045533/main/first/561/1.jpg")
    #     ]
    #     db.session.add_all(sample_clothes)
    #     db.session.commit()

# ==========================================
# 2. 網頁路由 (給人看的介面)
# ==========================================

# 【R】讀取 - 首頁 (包含穿搭推薦)
@app.route('/')
def home():
    clothes = Clothing.query.all()
    
    # 穿搭推薦邏輯
    tops = Clothing.query.filter_by(category='上衣').all()
    bottoms = Clothing.query.filter_by(category='褲子').all()
    
    recommended_top = random.choice(tops) if tops else None
    recommended_bottom = random.choice(bottoms) if bottoms else None

    return render_template(
        'show.html', 
        items=clothes,
        rec_top=recommended_top,
        rec_bottom=recommended_bottom
    )

# 【D】刪除 - 移除衣服
@app.route('/delete/<int:id>', methods=['POST'])
def delete_clothing(id):
    item_to_delete = Clothing.query.get_or_404(id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

# ==========================================
# 3. API 路由 (給機器人 Jetson Nano 傳資料用的)
# ==========================================

# 【C】新增 - 接收硬體端傳來的 JSON 資料
@app.route('/api/add_clothes', methods=['POST'])
def api_add_clothes():
    # 1. 接收 Nano 傳過來的資料
    data = request.get_json()
    
    # 2. 安全檢查
    if not data or 'name' not in data or 'category' not in data:
        return jsonify({'error': '缺少必要的衣服資料'}), 400
    
    # 3. 建立並存入資料庫
    new_cloth = Clothing(
        name=data['name'],
        category=data['category'],
        color=data.get('color', '未分類'),
        image_url=data.get('image_url', '')
    )
    
    db.session.add(new_cloth)
    db.session.commit()
    
    # 4. 回傳成功訊息給硬體
    return jsonify({
        'status': 'success',
        'message': f"成功將 {data['name']} 加入衣櫥！",
        'id': new_cloth.id
    }), 201

# ==========================================
# 4. 啟動伺服器
# ==========================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
