import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://nginxawsapp.icu"}})

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    raise Exception("Missing database environment variables")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("DB initialization error:", e)

@app.route("/health")
def health():
    return "Healthy", 200

@app.route("/")
def home():
    return "OK", 200

@app.route("/api/entries", methods=["POST"])
def add_entry():
    data = request.get_json()
    content = data.get("content") if data else None
    if not content or len(content) > 200:
        return jsonify({"error": "Content must be 1-200 chars"}), 400
    entry = Entry(content=content)
    db.session.add(entry)
    db.session.commit()
    return jsonify({"id": entry.id, "content": entry.content}), 201

@app.route("/api/entries", methods=["GET"])
def list_entries():
    entries = Entry.query.order_by(Entry.id.desc()).all()
    return jsonify([{"id": e.id, "content": e.content} for e in entries]), 200

@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    entry = Entry.query.get(entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"status": "deleted", "id": entry_id}), 200
    return jsonify({"error": "Entry not found"}), 404

@app.route("/api/test-db", methods=["GET"])
def test_db():
    try:
        entries = Entry.query.all()
        return jsonify([{"id": e.id, "content": e.content} for e in entries])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

