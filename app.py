from flask import Flask, flash, redirect, render_template, request, session
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
    page = session.get("page", 1)

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # get pages
    try:
        cursor.execute(f"SELECT * FROM pages WHERE id = {page}")
    except sqlite3.Error as e:
        app.logger.info(f"ERROR at get_dots: {e}")
    pages = dict(cursor.fetchone())

    # get dots
    try:
        cursor.execute(f"SELECT * FROM dots WHERE page_id = {page}")
    except sqlite3.Error as e:
        app.logger.info(f"ERROR at get_dots: {e}")
    dots = [dict(row) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template("index.html", dots=dots, pages=pages)


@app.route('/increment', methods=['POST'])
def increment():

    action = request.form.get("action")
    if action == "prev" and session.get("page", 1) > MIN:
        page = session.get("page", 1) - 1
        session["page"] = page
    elif action == "next" and session.get("page", 1) < MAX:
        page = session.get("page", 1) + 1
        session["page"] = page

    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)