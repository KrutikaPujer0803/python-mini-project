from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "lifeos"

DB = "database.db"

def db():
    return sqlite3.connect(DB)

# CREATE DATABASE
if not os.path.exists(DB):
    c = db()
    c.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
    c.execute("CREATE TABLE tasks(id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, deadline TEXT)")
    c.execute("CREATE TABLE habits(id INTEGER PRIMARY KEY, user_id INTEGER, habit TEXT)")
    c.execute("CREATE TABLE expenses(id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, category TEXT)")
    c.commit()
    c.close()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        c = db()
        user = c.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (request.form["email"], request.form["password"])
        ).fetchone()
        c.close()
        if user:
            session["uid"] = user[0]
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        c = db()
        c.execute("INSERT INTO users VALUES(NULL,?,?)",
                  (request.form["email"], request.form["password"]))
        c.commit()
        c.close()
        return redirect("/")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "uid" not in session:
        return redirect("/")
    c = db()
    tasks = c.execute("SELECT * FROM tasks WHERE user_id=?", (session["uid"],)).fetchall()
    habits = c.execute("SELECT * FROM habits WHERE user_id=?", (session["uid"],)).fetchall()
    expenses = c.execute("SELECT * FROM expenses WHERE user_id=?", (session["uid"],)).fetchall()
    c.close()
    return render_template("dashboard.html", tasks=tasks, habits=habits, expenses=expenses)

@app.route("/add_task", methods=["POST"])
def add_task():
    c = db()
    c.execute("INSERT INTO tasks VALUES(NULL,?,?,?)",
              (session["uid"], request.form["title"], request.form["deadline"]))
    c.commit()
    c.close()
    return redirect("/dashboard")

@app.route("/add_habit", methods=["POST"])
def add_habit():
    c = db()
    c.execute("INSERT INTO habits VALUES(NULL,?,?)",
              (session["uid"], request.form["habit"]))
    c.commit()
    c.close()
    return redirect("/dashboard")

@app.route("/add_expense", methods=["POST"])
def add_expense():
    c = db()
    c.execute("INSERT INTO expenses VALUES(NULL,?,?,?)",
              (session["uid"], request.form["amount"], request.form["category"]))
    c.commit()
    c.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)