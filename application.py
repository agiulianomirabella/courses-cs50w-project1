import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#no se si esto va aquí
# Tell Flask what SQLAlchemy databas to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Link the Flask app with the database (no Flask app is actually being run yet).
db.init_app(app)

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

        if password != password1:
            return render_template("errors/register_error.html", message="Passwords don't match. Please try again")

        #check if email is already in db
        user1 = User.query.filter_by(email = email).first()
        if user1 is not None:
            return render_template("errors/register_error1.html", email="{}".format(email))

        user2 = User.query.filter_by(username = username).first()
        if user2 is not None:
            return render_template("errors/register_error.html", message="{} username already exists. Please try with another username".format(username))
        
        #inserting the new user into the db:
        user = User(name=name, email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()

    except ValueError:
        return render_template("errors/register_error.html", message="Something went wrong, please introduce a name, username and password to register")
    return render_template("successes/register_success.html", name = name)

@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.form.get("username")
        password = int(request.form.get("password"))
        user = User.query.filter_by(username=username).first()

        if user is None:
            return render_template("errors/login_error.html", message="Sorry, there is no user with such username. Please try again")

        if password != user.password:
            return render_template("errors/login_error.html", message="Sorry, the password is incorrect. Please try again")

    except ValueError:
        return render_template("errors/login_error.html", message="Something went wrong, please introduce correctly your email or username and password to log in.")

    session["id"] = user.id
    return render_template("successes/login_success.html", name = user.name)

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/books", methods=["POST"])
def books():
    books = []
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        books = books + Book.query.filter_by(title = title).all()
        books = books + Book.query.filter_by(author = author).all()
        books = books + Book.query.filter_by(isbn = isbn).all()
        if not books:
            return render_template("errors/search_error.html", message= "No book with such properties.")
        return render_template("books.html", books = books)
    except ValueError:
        return render_template("errors/search_error.html", message= "We are sorry, something went wrong.")

@app.route("/books/<int:book_id>")
def book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return render_template("errors/search_error.html", message= "We are soory, there's no such book.")
    reviews = Review.query.filter_by(book_id = book_id).all()
    return render_template("book.html", book = book, reviews = reviews)


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