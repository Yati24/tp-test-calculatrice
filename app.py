import sqlite3
from flask import Flask, g, jsonify, request, render_template
from calculator import core

DB_PATH = "history.db"

app = Flask(__name__, static_folder="static", template_folder="templates")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            a REAL NOT NULL,
            b REAL NOT NULL,
            op TEXT NOT NULL,
            result REAL NOT NULL,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calc", methods=["POST"])
def api_calc():
    data = request.get_json() or {}
    a = float(data.get("a", 0))
    b = float(data.get("b", 0))
    op = data.get("op", "+")

    func_map = {
        "+": core.add,
        "-": core.subtract,
        "*": core.multiply,
        "/": core.divide,
    }

    if op not in func_map:
        return jsonify({"error": "problème d'opération"}), 400

    try:
        result = func_map[op](a, b)
    except ZeroDivisionError:
        return jsonify({"error": "division par zero"}), 400

    db = get_db()
    c = db.cursor()
    c.execute(
        "INSERT INTO history (a, b, op, result) VALUES (?, ?, ?, ?)",
        (a, b, op, float(result)),
    )
    db.commit()

    return jsonify({"result": result})


@app.route("/api/history", methods=["GET"])
def api_history():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, a, b, op, result, ts FROM history ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    data = [dict(r) for r in rows]
    return jsonify(data)


@app.route("/api/history/clear", methods=["POST"])
def api_history_clear():
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM history")
    db.commit()
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
