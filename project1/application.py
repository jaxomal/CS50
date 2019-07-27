import os

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
    return signin()

@app.route("/signin")
def signin():
	return render_template("signin.html")

@app.route("/create")
def create():
	return render_template("create.html")

@app.route("/login", methods=["POST"])
def login():
	"""Log into your account."""

    # Get form information
    username = request.form.get("username")
    password = request.form.get("password")

def create():
    """Create an account."""

def logout():
    """Log out of your account."""

if __name__ == '__main__':
    app.run(host='0.0.0.0')