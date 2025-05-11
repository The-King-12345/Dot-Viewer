from flask import Flask, flash, redirect, render_template, jsonify, request, session
from flask_session import Session
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename
from populate_upload import pdf_to_populate, create_tables, populate, add_timestamps, add_holds  

POP2024_DB = "static/PoP/24database.db"
POP2023_DB = "static/PoP/23database.db"
POP2022_DB = "static/PoP/22database.db"
POP2021_DB = "static/PoP/21database.db"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.config["USER_DB_FOLDER"] = "user_databases"
os.makedirs(app.config["USER_DB_FOLDER"], exist_ok=True)

def get_session_upload_folder():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    
    session_folder = os.path.join(app.config["UPLOAD_FOLDER"], session["session_id"])
    os.makedirs(session_folder, exist_ok=True)
    return session_folder

def get_user_db():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    
    db_path = os.path.join(app.config["USER_DB_FOLDER"], f"{session['session_id']}.db")
    return db_path

@app.route("/", methods=["GET"])
def index():
    session["db_path"] = POP2024_DB
    return render_template("index.html")

@app.route("/PoP2024", methods=["GET"])
def PoP2024():
    session["db_path"] = POP2024_DB
    return render_template("viewer.html")

@app.route("/PoP2023", methods=["GET"])
def PoP2023():
    session["db_path"] = POP2023_DB
    return render_template("viewer.html")

@app.route("/PoP2022", methods=["GET"])
def PoP2022():
    session["db_path"] = POP2022_DB
    return render_template("viewer.html")

@app.route("/PoP2021", methods=["GET"])
def PoP2021():
    session["db_path"] = POP2021_DB
    return render_template("viewer.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "pdf" not in request.files:
            return redirect(request.url)

        file = request.files["pdf"]
        if file.filename == "":
            return redirect(request.url)

        if file and "." in file.filename and file.filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]:
            session_folder = get_session_upload_folder()
            filename = secure_filename(file.filename)
            filepath = os.path.join(session_folder, filename)
            file.save(filepath)

            
            db_path = get_user_db()
            create_tables(db_path)
            
            pdf_to_populate(filepath, db_path) #populates
            add_timestamps(db_path, 0, [[160, 1, 1]], {}) # startDelay, tempos, delays
            add_holds(db_path, []) # holds


            # store db_path
            session["db_path"] = db_path

            return render_template("viewer.html")

    return render_template("upload.html")

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

    return jsonify([dots, pages, performers])


if __name__ == "__main__":
    app.run(debug=True)