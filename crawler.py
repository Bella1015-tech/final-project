import requests
from app import app, db, Clothing

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

print("🕷️ 開始爬取商品...")

with app.app_context():
    db.create_all()
    
    # 清空舊資料
    db.session.query(Clothing).delete()
    db.session.commit()
    print("🗑️ 清空舊資料")
    
    total_added = 0
    for api_category, display_category in CATEGORIES:
        url = f"https://dummyjson.com/products/category/{api_category}"
        response = requests.get(url)
        
        if response.status_code == 200:
            products = response.json()['products']
            print(f"✅ 抓取 {display_category} ({len(products)} 件)")
            
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
    print(f"🎉 成功新增 {total_added} 件衣服！")