from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ml_utils.eval_utils import predict_from_url

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_history.db'
db = SQLAlchemy(app)

# --- Cấu trúc bảng lưu lịch sử ---
class URLHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    model_used = db.Column(db.String(50))
    prediction = db.Column(db.Integer)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Khởi tạo database ---
with app.app_context():
    db.create_all()

# --- Trang chủ: nhập URL và dự đoán ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url").strip()

        # Dự đoán dựa trên URL thật
        pred, conf, features = predict_from_url(url, model_path="models/rf_model.pkl")

        # Kết quả hiển thị
        result = "✅ URL an toàn" if pred == 1 else "⚠️ URL không an toàn"
        conf_display = round(conf * 100, 2) if conf is not None else None

        # Lưu vào database
        record = URLHistory(
            url=url,
            model_used="RandomForest",
            prediction=pred,
            confidence=conf
        )
        db.session.add(record)
        db.session.commit()

        # Hiển thị ra trang kết quả
        return render_template("detail.html",
                               url=url,
                               result=result,
                               confidence=conf_display,
                               features=features)

    return render_template("index.html")

# --- Trang xem lịch sử ---
@app.route("/history")
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # số bản ghi mỗi trang

    # Sắp theo ID giảm dần (mới nhất lên đầu)
    pagination = URLHistory.query.order_by(URLHistory.id.asc()).paginate(page=page, per_page=per_page)

    # Không đảo lại nữa nhé
    items = pagination.items

    return render_template("history.html", pagination=pagination, items=items)

@app.route("/detail/<int:record_id>")
def detail(record_id):
    record = URLHistory.query.get_or_404(record_id)

    # Nếu bạn chưa lưu features, có thể dự đoán lại:
    _, _, features = predict_from_url(record.url, model_path="models/rf_model.pkl")

    conf_display = round(record.confidence * 100, 2) if record.confidence else None
    result = "✅ URL an toàn" if record.prediction == 1 else "⚠️ URL không an toàn"

    return render_template(
        "detail.html",
        url=record.url,
        result=result,
        confidence=conf_display,
        features=features
    )

if __name__ == "__main__":
    app.run(debug=True)
