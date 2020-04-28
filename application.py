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

        if "" in [name, email, username, password, password1]:
            return render_template("errors/register_error.html", message="Please dont't leave blank spaces.")

        if password != password1:
            return render_template("errors/register_error.html", message="Passwords don't match. Please try again.")

        #check if email is already in db
        user1 = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
        if user1 is not None:
            return render_template("errors/register_error_email.html", email="{}".format(email))

        #check if username already exists
        user2 = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if user2 is not None:
            return render_template("errors/register_error.html", message="{} username already exists. Please try with another username.".format(username))
        
        #inserting the new user into the db:
        db.execute("INSERT INTO users (name, email, username, password) VALUES (:name, :email, :username, :password)",
            {"name":name, "email":email, "username":username, "password":password}
        )
        db.commit()

    except ValueError:
        return render_template("errors/register_error.html", message="Something went wrong, please introduce a name, username and password to register")
    return render_template("successes/register_success.html", name = name)

@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.form.get("username")
        password = int(request.form.get("password"))
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if user is None:
            return render_template("errors/login_error.html", message="Sorry, there is no user with such username. Please try again")

        if password != user.password:
            return render_template("errors/login_error.html", message="Sorry, the password is incorrect. Please try again")

    except ValueError:
        return render_template("errors/login_error.html", message="Something went wrong, please introduce correctly your email or username and password to log in.")

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
        books = books + db.execute("SELECT * FROM books WHERE isbn LIKE '%{}}%'".format(isbn)).fetchall()
    if not books:
        return render_template("errors/search_error.html", message= "No book with such properties.")
    return render_template("books.html", books = books)

@app.route("/books/<int:book_id>")
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("errors/search_error.html", message= "We are soory, there's no such book.")

    reviews = db.execute(
        "SELECT reviews.*, users.username FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id",
        {"book_id": book_id}).fetchall()
    return render_template("book.html", book = book, reviews = reviews)

@app.route("/submit_review/<int:book_id>", methods=["POST"])
def submit_review(book_id):
    try:
        rating = int(request.form.get('rating'))
        text = request.form.get('text')
    except ValueError:
        return render_template("errors/review_errors.html", message= "Something went wrong.")
    
    exists = db.execute("SELECT * FROM reviews WHERE user_id = {} AND book_id = {}".format(session["id"], book_id)).fetchone()
    if not (exists is None):
        book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id":book_id}).fetchone()
        return render_template("errors/review_error.html", message= "Sorry, you can't submit two reviews for the same book.", book= book)
    
    db.execute("INSERT INTO reviews (rating, text, user_id, book_id) VALUES (:rating, :text, :user_id, :book_id)", {"rating":rating, "text":text, "user_id":session["id"], "book_id":book_id})
    db.commit()
    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id":book_id}).fetchone()
    return render_template("successes/review_success.html", book= book)


'''
@app.route("/book", methods=["POST"])
def book():
    """Book a flight."""

    # Get form information.
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")

    # Make sure flight exists.
    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        return render_template("error.html", message="No such flight with that id.")
    db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
            {"name": name, "flight_id": flight_id})
    db.commit()
    return render_template("success.html")

@app.route("/flights")
def flights():
    """Lists all flights."""
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("flights.html", flights=flights)

@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    """Lists details about a single flight."""

    # Make sure flight exists.
    flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
    if flight is None:
        return render_template("error.html", message="No such flight.")

    # Get all passengers.
    passengers = db.execute("SELECT name FROM passengers WHERE flight_id = :flight_id",
                            {"flight_id": flight_id}).fetchall()
    return render_template("flight.html", flight=flight, passengers=passengers)
'''