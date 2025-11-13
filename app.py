from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# -------------------------------
# Firebase 初期化
# -------------------------------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# -------------------------------
# ホームページ（バーコードスキャン）
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -------------------------------
# バーコード受信 & DB 登録
# -------------------------------
@app.route('/scan', methods=['POST'])
def scan_barcode():
    data = request.json
    barcode = data.get('barcode')
    
    if not barcode:
        return jsonify({"error": "barcode missing"}), 400
    
    # DB で既存チェック
    docs = db.collection("reagents").where("barcode","==",barcode).get()
    if docs:
        reagent = docs[0].to_dict()
        return jsonify({"status": "exists", "data": reagent})
    else:
        # 新規登録用の初期情報
        return jsonify({"status": "new", "barcode": barcode})

# -------------------------------
# 新規登録
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    barcode = data.get('barcode')
    name = data.get('name')
    qty = data.get('qty')
    expiration = data.get('expiration')
    
    if not all([barcode, name, qty, expiration]):
        return jsonify({"error": "missing fields"}), 400
    
    db.collection("reagents").add({
        "barcode": barcode,
        "name": name,
        "qty": qty,
        "expiration": expiration,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    return jsonify({"status": "registered"})
    

if __name__ == '__main__':
    app.run(debug=True)
