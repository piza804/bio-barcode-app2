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
# ルートページ
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------
# バーコード受信・登録
# -------------------------------
@app.route("/scan", methods=["POST"])
def scan():
    data = request.json
    barcode = data.get("barcode")
    if not barcode:
        return jsonify({"status":"error","message":"バーコードがありません"}), 400

    # Firestoreに既存か確認
    docs = db.collection("reagents").where("barcode","==",barcode).get()
    if docs:
        doc = docs[0]
        new_qty = doc.to_dict().get("qty",0) + 1
        db.collection("reagents").document(doc.id).update({
            "qty": new_qty,
            "updated_at": datetime.now()
        })
        action = "更新"
    else:
        # 新規登録（仮の名前・数量1）
        doc_ref = db.collection("reagents").add({
            "barcode": barcode,
            "name": f"新規試薬 {barcode}",
            "qty": 1,
            "expiration": "",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        action = "新規登録"

    return jsonify({"status":"ok","action":action, "barcode":barcode})

if __name__ == "__main__":
    app.run(debug=True)
