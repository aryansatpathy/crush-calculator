from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
ADMIN_PASSWORD = "aryan123"
DB = "crushes.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, name1 TEXT, name2 TEXT, percentage INTEGER, created_at TEXT)")
    con.commit()
    con.close()

def calculate_love(a, b):
    text = (a.strip().lower() + b.strip().lower())
    score = sum((i + 1) * ord(c) for i, c in enumerate(text) if c.isalpha())
    return 40 + score % 61

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    name1 = name2 = ""
    if request.method == "POST":
        name1 = request.form.get("name1", "").strip()
        name2 = request.form.get("name2", "").strip()
        if name1 and name2:
            result = calculate_love(name1, name2)
            con = sqlite3.connect(DB)
            con.execute("INSERT INTO submissions (name1,name2,percentage,created_at) VALUES (?,?,?,?)",
                        (name1, name2, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            con.commit()
            con.close()
    return render_template("index.html", result=result, name1=name1, name2=name2)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        if request.method == "POST":
            if request.form.get("password") == ADMIN_PASSWORD:
                session["admin"] = True
                return redirect(url_for("admin"))
            return render_template("admin_login.html", error="Incorrect password.")
        return render_template("admin_login.html")
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM submissions ORDER BY id DESC").fetchall()
    con.close()
    return render_template("admin.html", rows=rows)

@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

init_db()
if __name__ == "__main__":
    app.run(debug=True)
