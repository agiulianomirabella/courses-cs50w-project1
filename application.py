import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

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

KEY= "DziaMb5DXMiwIBK5df6w"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register_form")
def register_form():
    return render_template("register_form.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        name = request.form.get("name").capitalize()
        email = request.form.get("email")
        username = request.form.get("username")
        password = int(request.form.get("password"))
        password1 = int(request.form.get("password1"))

    except ValueError:
        return render_template("errors/register_error.html", message="Something went wrong, please introduce a name, username and password to register, do not leave blank spaces.")

    if "" in [name, email, username, password, password1]:
        return render_template("errors/register_error.html", message="Please do not leave blank spaces.")

    if password != password1:
        return render_template("errors/register_error.html", message="Passwords don't match. Please try again.")

    #check if email is already in db
    user1 = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
    if user1 is not None:
        return render_template("errors/register_error_email.html", email="{}".format(email))

    #check if username already exists
    user2 = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    if user2 is not None:
        return render_template("errors/register_error.html", message="Username: {} already exists. Please try with another username.".format(username))
    
    #inserting the new user into the db:
    db.execute("INSERT INTO users (name, email, username, password) VALUES (:name, :email, :username, :password)",
        {"name":name, "email":email, "username":username, "password":password}
    )
    db.commit()
    user = db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).fetchone()
    session["id"] = user.id
    return render_template("successes/register_success.html", name = name)

@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.form.get("username")
        password = int(request.form.get("password"))
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    except ValueError:
        return render_template("errors/login_error.html", message="Something went wrong, please introduce correctly your email or username and password to log in.")

    if user is None:
        return render_template("errors/login_error.html", message="Sorry, there is no user with such username.")

    if password != user.password:
        return render_template("errors/login_error.html", message="Sorry, the password is incorrect. Please try again")

    session["id"] = user.id
    return render_template("successes/login_success.html", name = user.name)

@app.route("/logout", methods= ["POST"])
def logout():
    session["id"] = None
    return render_template("logout.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/books", methods= ["POST"])
def books():
    books = []
    try:
        title = request.form.get('title').lower()
        author = request.form.get('author').lower()
        isbn = request.form.get('isbn')
    except ValueError:
        return render_template("errors/search_error.html", message= "We are sorry, something went wrong.")
    if title != "":
        books = books + db.execute("SELECT * FROM books WHERE lower(title) LIKE '%{}%'".format(title)).fetchall()
    if author != "":
        books = books + db.execute("SELECT * FROM books WHERE lower(author) LIKE '%{}%'".format(author)).fetchall()
    if isbn != "":
        books = books + db.execute("SELECT * FROM books WHERE isbn LIKE '%{}%'".format(isbn)).fetchall()
    if not books:
        return render_template("errors/search_error.html", message= "No book with such properties.")
    return render_template("books.html", books = books)

@app.route("/books/<int:book_id>", methods= ["GET", "POST"])
def book(book_id):
    if request.method == "POST":
        try:
            rating = int(request.form.get('rating'))
            text = request.form.get('text')
        except ValueError:
            return render_template("errors/review_error.html", message= "Something went wrong.")
        
        exists = db.execute("SELECT * FROM reviews WHERE user_id = {} AND book_id = {}".format(session["id"], book_id)).fetchone()
        if not (exists is None):
            book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id":book_id}).fetchone()
            return render_template("errors/review_error.html", message= "Sorry, you can't submit two reviews for the same book.", book= book)
        
        db.execute("INSERT INTO reviews (rating, text, user_id, book_id) VALUES (:rating, :text, :user_id, :book_id)", {"rating":rating, "text":text, "user_id":session["id"], "book_id":book_id})
        db.commit()

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("errors/search_error.html", message= "We are sorry, there's no such book.")

    reviews = db.execute(
        "SELECT reviews.*, users.username FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id",
        {"book_id": book_id}).fetchall()

    available = False
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": [book.isbn]})
    if res.status_code == 200:
        avg = res.json()["books"][0]["average_rating"]
        available = True

    return render_template("book.html", book = book, reviews = reviews, avg = avg, available = available)

@app.route("/api/books/<int:book_id>")
def book_api(book_id):
    # Check the book exists.
    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id":book_id}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid book_id"}), 404

    # Get all reviews
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id":book_id}).fetchall()

    if len(reviews) == 0:
        avg = None
    else:
        avg = sum([review.rating for review in reviews])/len(reviews)

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": len(reviews),
        "average_score": avg
        })

@app.route("/account/")
def account():
    reviewed = db.execute("SELECT reviews.*, books.title FROM reviews JOIN books ON reviews.book_id = books.id WHERE user_id = :session_id ORDER BY id DESC", {"session_id":session["id"]}).fetchall()
    user = db.execute("SELECT * FROM users WHERE id = :session_id", {"session_id":session["id"]}).fetchone()
    return render_template("account.html", user= user, reviewed = reviewed)
