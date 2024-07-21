from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3
import logging

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# global variable sets
sets = 0
MAX = 28

@app.route("/", methods=["GET", "POST"])
def index():
    global sets

    if request.method == "POST":
        action = request.form.get('action')
        if action == "prev" and sets > 0:
            sets -= 1
        elif action == "next" and sets < MAX:
            sets += 1
        
        return redirect("/")
    
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM performers WHERE sets={sets}")
        rows = cursor.fetchall()
        dots = [dict(row) for row in rows]

        cursor.close()
        conn.close()

        return render_template("index.html", dots=dots, sets=sets)

if __name__ == '__main__':
    app.run(debug=True)