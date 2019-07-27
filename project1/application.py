import os
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("in"):
        return bookstore()
    else:
        return signin()

@app.route("/bookstore")
def bookstore():
    if not session.get("in"):
        render_template("error.html", message="You are not signed in")
    else:
        render_template("bookstore.html", message="Logged in")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/create")
def create():
    return render_template("create.html")

@app.route("/login", methods=["POST"])
def login():
    """Log into your account."""
    id = int(request.form.get("id"))
    username = request.form.get("username")
    password = request.form.get("password")

    res = db.execute("SELECT username, password FROM users WHERE id = :id", {"id": id}).fetchone()
    """Perform check on the user"""
    if res is None:
        return render_template("error.html", message="No such id")
    if res.username != username or res.password != password:
        return render_template("error.html", message="Invalid password or username")
    session["in"] = True
    session["id"] = id
    return index()

@app.route("/register", methods=["POST"])
def register():
    """Create an account."""
    user = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")
    if password != password_confirm:
        return create()
    """Check if a user already exists"""
    res = db.execute("SELECT username FROM users WHERE username = :user", {"user": user}).fetchone()
    if res is not None:
        return render_template("error.html", message="Username already exists")
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": user, "password": password})
    id = int(db.execute("SELECT id FROM users WHERE username = :user", {"user": user}).fetchone().id)
    db.commit()
    return render_template("success.html", message="Your id is " + str(id))

@app.route("/logout")
def logout():
    """Log out of your account."""
    session["in"] = False
    session["id"] = None

if __name__ == '__main__':
    app.run(host='0.0.0.0')