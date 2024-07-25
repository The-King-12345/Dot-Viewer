from flask import Flask, flash, redirect, render_template, jsonify, request, session
from flask_session import Session
import sqlite3

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# global variable 
MIN = 1
MAX = 30

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/positions", methods=["GET"])
def positions():
    page_id = request.args.get("page_id", default = 1, type=int)

    conn = sqlite3.connect("static/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM dots WHERE page_id = {page_id}")
    except sqlite3.Error as e:
        app.logger.info(f"ERROR at get_dots: {e}")
    dots = [dict(row) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return jsonify(dots)

# @app.route("/save_index", methods=["POST"])
# def save_index():
#     data = request.get_json()
#     session["page"] = data["current_index"]
#     return jsonify({"status": "success", "current_index": session["page"]})


if __name__ == "__main__":
    app.run(debug=True)