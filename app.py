from flask import Flask, flash, redirect, render_template, jsonify, request, session
from flask_session import Session
import sqlite3

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/database", methods=["GET"])
def get_data():
    conn = sqlite3.connect("static/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM dots")
    except sqlite3.Error as e:
        app.logger.info(f"ERROR at /positions: {e}")
    dots = [dict(row) for row in cursor.fetchall()]

    try:
        cursor.execute(f"SELECT * FROM pages")
    except sqlite3.Error as e:
        app.logger.info(f"ERROR at /positions: {e}")
    pages = [dict(row) for row in cursor.fetchall()]

    try:
        cursor.execute(f"SELECT * FROM performers")
    except sqlite3.Error as e:
        app.logger.info(f"ERROR at /positions: {e}")
    performers = [dict(row) for row in cursor.fetchall()]

    return jsonify([dots, pages, performers])


if __name__ == "__main__":
    app.run(debug=True)