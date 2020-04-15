import os

from flask import Flask, render_template, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_session import Session

app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register_form")
def register_form():
    print("HOLA")
    return render_template("register_form.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        name = request.form.get("name").capitalize()
        email = request.form.get("email")
        username = request.form.get("username")
        password = int(request.form.get("password"))
        password1 = int(request.form.get("password1"))

        #check everything is correct:
        if name is None or username is None or password is None or password1 is None:
            return render_template("register_error.html", message="Please type correctly your name, email, username, and password")

        if password != password1:
            return render_template("register_error.html", message="Passwords don't match. Please try again")
        user = db.execute("SELECT * FROM users WHERE users.email=:email", {'email':email}).fetchone()
        if user is not None:
            return render_template("register_error1.html", email="{}".format(email))
        user = db.execute("SELECT * FROM users WHERE users.username=:username", {'username':username}).fetchone()
        if user is not None:
            return render_template("register_error.html", message="{} already exists. Please try with another username".format(username))
        
        #inserting the new user into the db:
        db.execute("INSERT INTO users (name, email, username, password) VALUES (:name, :email, :username, :password)",
            {"name":name, "email": email, "username":username, "password":password})
        db.commit()

    except ValueError:
        return render_template("register_error.html", message="Something went wrong, please introduce a name, username and password to register")
    return render_template("register_success.html", name = name)

@app.route("/login", methods=["POST"])
def login():
    try:
        target = request.form.get("target")
        password = int(request.form.get("password"))

        #check everything is correct:
        if target is None or password is None:
            return render_template("login_error.html", message="Please type correctly your username or email and your password.")

        user = db.execute("SELECT * FROM users WHERE users.email=:target", {'target':target}).fetchone()
        if user is None:
            user = db.execute("SELECT * FROM users WHERE users.username=:target", {'target':target}).fetchone()
            if user is None:
                return render_template("login_error1.html")

        if password != user.password:
            return render_template("login_error2.html")
        
        session['id'] = user.id

    except ValueError:
        return render_template("login_error.html", message="Something went wrong, please introduce correctly your email or username and password to log in.")
    return render_template("login_success.html", name = user.name)

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/books", methods=["POST"])
def books():
    try:
        title = request.form.get('title')
        books = db.execute("SELECT * from books WHERE books.title = :title", {'title':title}).fetchall()
        if title == '':
            author = request.form.get('author')
            books = db.execute("SELECT * from books WHERE books.author = :author", {'author':author}).fetchall()
            if author == '':
                isbn = request.form.get('isbn')
                books = db.execute("SELECT * from books WHERE books.isbn = :isbn", {'isbn':isbn}).fetchall()
            else:
                return render_template("search_error.html", message= "Please, fill at least one field to search the book succesfully.")
        return render_template("books.html", books = books)
    except ValueError:
        return render_template("search_error.html", message= "We are sorry, something went wrong.")

@app.route("/books/<int:book_id>")
def book(book_id):
    try:
        book = db.execute("SELECT * FROM books WHERE books.id=:book_id", {"book_id":book_id}).fetchone()
        return render_template("book.html", book = book)
    except:
        return render_template("search_error.html", message= "We are sorry, something went wrong.")


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