import csv
import os

from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

os.environ['DATABASE_URL'] = 'postgresql://wfwoewdbugkurk:85896f0531941d15a43b9b864b47376882347a56b7d19161fb044850141b8ebe@ec2-54-217-204-34.eu-west-1.compute.amazonaws.com:5432/d2ldkrsktl45l4'
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    delete_tables()
    create_tables()
    import_books()
    import_users()
    books, users = show_tables()
    return render_template("index.html", books = books, users = users)

def delete_tables():
    db.execute("DROP SCHEMA public CASCADE;")
    db.execute("CREATE SCHEMA public;")
    db.execute("GRANT ALL ON SCHEMA public TO postgres;")
    db.execute("GRANT ALL ON SCHEMA public TO public;")
    db.commit()

def create_tables():
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL);")
    db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, email VARCHAR NOT NULL, username VARCHAR NOT NULL, password INTEGER NOT NULL);")
    db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, rating INTEGER NOT NULL, text VARCHAR NOT NULL, book_id INTEGER REFERENCES books, user_id INTEGER REFERENCES users)")
    db.commit()

def import_books():
    f = open("booksTest.csv")
    #f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn":isbn, "title":title, "author":author, "year":year})
    db.commit()

def import_users():
    f = open("users.csv")
    reader = csv.reader(f)
    for name, email, username, password in reader:
        db.execute("INSERT INTO users (name, email, username, password) VALUES (:name, :email, :username, :password)",
                    {"name":name, "email":email, "username":username, "password":password})
    db.commit()

def show_tables():
    books = db.execute("SELECT * from books LIMIT 10").fetchall()
    users = db.execute("SELECT * from users LIMIT 10").fetchall()
    return books, users
