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
    session["username"] = username
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
    session["username"] = None
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
    if request.method == "GET":
        res = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_id}).fetchone()
        if (res is None):
            return render_template("error.html", message="messed up")
        book_isbn = res.isbn
        title = res.title
        author = res.author
        year = res.year
        review_count = res.review_count
        all_reviews = reviews(book_id)
        return render_template("book.html", book_isbn=book_isbn, title=title, author=author, year=year, review_count=review_count, reviews=all_reviews)
    else:
        rating = request.form.get("rating")
        review = request.form.get("review")
        poster = session.get("username")
        db.execute("INSERT INTO REVIEWS (book_id, poster, review) VALUES (:book_id, :poster, :review)",
            {"book_id": book_id, "poster": poster, "review": review})
        review_count = int(db.execute("SELECT review_count FROM books WHERE isbn = :isbn", {"isbn": book_id}).fetchone().review_count) + 1
        db.execute("UPDATE books SET review_count = :review_count WHERE isbn = :isbn", {"review_count" : review_count, "isbn": book_id})
        db.commit()
        return render_template("success.html", message="You have posted a review")


def reviews(isbn):
    res = db.execute("SELECT poster, review FROM reviews JOIN books ON book_id = books.isbn WHERE isbn = :isbn",
        {"isbn": isbn})
    return res;

if __name__ == '__main__':
    app.run(host='0.0.0.0')