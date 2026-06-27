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

database_url = os.environ.get('DATABASE_URL', 'sqlite:///wardrobe.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 建立資料庫模型 - 衣服
class Clothing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=True)  
    image_url = db.Column(db.String(300), nullable=True) 

# 資料庫初始化
with app.app_context():
    db.create_all()
    
    # 首次部署時自動爬蟲 - 強制清空舊資料
    db.session.query(Clothing).delete()
    db.session.commit()
    
    print("🕷️ 首次部署，自動填充資料...")
    import requests
    
    CATEGORIES = [
        ('womens-dresses', '洋裝'),
        ('tops', '上衣'),
        ('womens-shoes', '鞋子'),
        ('mens-shirts', '襯衫'),
        ('womens-bags', '包包'),
        ('womens-jewellery', '飾品'),
        ('sunglasses', '太陽眼鏡'),
        ('womens-watches', '手錶'),
    ]
    
    total_added = 0
    for api_category, display_category in CATEGORIES:
        url = f"https://dummyjson.com/products/category/{api_category}"
        response = requests.get(url)
        
        if response.status_code == 200:
            products = response.json()['products']
            for item in products:
                new_clothes = Clothing(
                    name=item['title'],
                    category=display_category,
                    color='未分類',
                    image_url=item['images'][0] if item.get('images') else ''
                )
                db.session.add(new_clothes)
                total_added += 1
    
    # 手動新增褲子
    MANUAL_ITEMS = [
        {'name': '黑色緊身褲', 'category': '褲子', 'image_url': 'https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400'},
        {'name': '淺藍牛仔褲', 'category': '褲子', 'image_url': 'https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400'},
        {'name': '米白色寬褲', 'category': '褲子', 'image_url': 'https://images.unsplash.com/photo-1552062407-291826de9e82?w=400'},
    ]
    
    for item in MANUAL_ITEMS:
        new_clothes = Clothing(
            name=item['name'],
            category=item['category'],
            color='未分類',
            image_url=item['image_url']
        )
        db.session.add(new_clothes)
        total_added += 1
    
    db.session.commit()
    print(f"✅ 自動填充完成，新增 {total_added} 件衣服")

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
# 3.5 體型分析路由
# ==========================================

def classify_body_type(bust, waist, hip):
    """根據三圍數據分類體型"""
    waist_hip_ratio = waist / hip
    bust_hip_diff = abs(bust - hip)
    
    if waist_hip_ratio < 0.75 and bust_hip_diff <= 5:
        return "沙漏型", "hourglass"
    elif hip > bust and waist_hip_ratio < 0.75:
        return "梨型", "pear"
    elif waist >= hip or (waist / bust) > 0.8:
        return "蘋果型", "apple"
    elif bust > hip + 3:
        return "倒三角型", "inverted_triangle"
    else:
        return "矩形", "rectangle"

STYLE_ADVICE = {
    "hourglass": {
        "優點": "腰線明顯，上下比例均衡",
        "建議": ["合身洋裝", "高腰裙", "V領上衣", "貼身針織"],
        "避免": ["寬鬆直筒版型", "過於蓬鬆的外套"]
    },
    "pear": {
        "優點": "臀部豐滿有曲線",
        "建議": ["A字裙", "深色下身", "亮色上衣", "船領/寬肩設計"],
        "避免": ["緊身褲", "低腰設計", "橫條紋下身"]
    },
    "apple": {
        "優點": "上半身豐滿、腿部修長",
        "建議": ["V領拉長頸部", "Empire腰線洋裝", "直筒長褲", "開襟外套"],
        "避免": ["高領", "緊身腰部設計", "腰帶強調"]
    },
    "inverted_triangle": {
        "優點": "肩膀寬闊有氣場",
        "建議": ["A字裙", "蓬裙", "細肩帶", "低領設計"],
        "避免": ["墊肩", "船領", "橫條紋上身"]
    },
    "rectangle": {
        "優點": "身材均勻、好搭配",
        "建議": ["腰帶創造腰線", "荷葉邊", "層次穿搭", "Peplum上衣"],
        "避免": ["完全直筒版型"]
    }
}

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    result = None
    if request.method == 'POST':
        try:
            bust = float(request.form['bust'])
            waist = float(request.form['waist'])
            hip = float(request.form['hip'])
            
            body_type_zh, body_type_key = classify_body_type(bust, waist, hip)
            advice = STYLE_ADVICE[body_type_key]
            
            result = {
                'body_type': body_type_zh,
                'bust': bust,
                'waist': waist,
                'hip': hip,
                'advice': advice
            }
        except (ValueError, ZeroDivisionError):
            result = {'error': '請輸入有效的數字'}
    
    return render_template('analyze.html', result=result)

# ==========================================
# 4. 啟動伺服器
# ==========================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)