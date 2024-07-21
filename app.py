from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3
import logging

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pass
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM performers WHERE sets=0")
        rows = cursor.fetchall()
        dots = [dict(row) for row in rows]

        cursor.close()
        conn.close()

        return render_template("index.html", dots=dots)

if __name__ == '__main__':
    app.run(debug=True)