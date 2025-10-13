from flask import Flask, render_template, jsonify, session
import sqlite3
import os

POP2024_DB = "static/PoP/24database.db"
POP2023_DB = "static/PoP/23database.db"
POP2022_DB = "static/PoP/22database.db"
POP2021_DB = "static/PoP/21database.db"

POP2024_MP3 = "static/PoP/24audio.mp3"
POP2023_MP3 = "static/PoP/23audio.mp3"
POP2022_MP3 = "static/PoP/22audio.mp3"
POP2021_MP3 = "static/PoP/21audio.mp3"
SILENT_MP3 = "static/PoP/silence.mp3"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

@app.route("/", methods=["GET"])
def index():
    session["db_path"] = POP2024_DB
    return render_template("index.html")

@app.route("/PoP2024", methods=["GET"])
def PoP2024():
    session["db_path"] = POP2024_DB
    return render_template("viewer.html", audio_path = POP2024_MP3)

@app.route("/PoP2023", methods=["GET"])
def PoP2023():
    session["db_path"] = POP2023_DB
    return render_template("viewer.html", audio_path = POP2023_MP3)

@app.route("/PoP2022", methods=["GET"])
def PoP2022():
    session["db_path"] = POP2022_DB
    return render_template("viewer.html", audio_path = POP2022_MP3)

@app.route("/PoP2021", methods=["GET"])
def PoP2021():
    session["db_path"] = POP2021_DB
    return render_template("viewer.html", audio_path = POP2021_MP3)

@app.route("/api/database", methods=["GET"])
def get_data():
    conn = sqlite3.connect(session["db_path"])
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

    # manually input holds [set,duration]
    holds = []

    if session["db_path"] == POP2024_DB:
        holds = [[23,60/107*7*1000], [37,60/160*4*1000]]
    elif session["db_path"] == POP2023_DB:
        holds = [[30,60/132*5.5*1000]]
    elif session["db_path"] == POP2022_DB:
        holds = [[50,60/164*16*1000]]
    elif session["db_path"] == POP2021_DB:
        holds = []
    
    return jsonify([dots, pages, performers, holds])


if __name__ == "__main__":
    app.run(debug=True)