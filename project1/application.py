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

class Book:
    def __init__(self, isbn, title, author, year):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.reviewcount = 0

@app.route("/")
def index():
    if session.get("in"):
        return bookstore()
    else:
        return signin()

@app.route("/bookstore")
def bookstore():
    if not session.get("in"):
        return render_template("error.html", message="You are not signed in")
    else:
        return render_template("bookstore.html")

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

@app.route("/logout", methods=["GET"])
def logout():
    """Log out of your account."""
    session["in"] = False
    session["id"] = None
    return signin()

@app.route("/search", methods=["GET", "POST"])
def search():
    # Look through the database for matching ISBN, title, or author return all results
    search_res = request.form.get("search")
    like_res = "'%" + search_res + "%'"
    res = db.execute("SELECT * FROM books WHERE isbn LIKE " + like_res + " OR title LIKE" +  like_res + " OR author LIKE" + like_res)
    if (res.rowcount == 0):
        return render_template("error.html", message="messed up")
    return render_template("results.html", books=res)

@app.route("/book/<book_id>", methods=["GET", "POST"])
def book(book_id):
    res = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_id}).fetchone()
    if (res is None):
        return render_template("error.html", message="messed up")
    currentBook = Book(res.isbn, res.title, res.author, res.year)
    book_isbn = currentBook.isbn
    title = currentBook.title
    author = currentBook.author
    year = currentBook.year
    review = currentBook.reviewcount
    return render_template("book.html", book_isbn=book_isbn, title=title, author=author, year=year, review=review)

if __name__ == '__main__':
    app.run(host='0.0.0.0')