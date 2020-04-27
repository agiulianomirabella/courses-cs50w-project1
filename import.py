import csv
import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
os.environ['DATABASE_URL'] = 'postgresql://wfwoewdbugkurk:85896f0531941d15a43b9b864b47376882347a56b7d19161fb044850141b8ebe@ec2-54-217-204-34.eu-west-1.compute.amazonaws.com:5432/d2ldkrsktl45l4'
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

'''
TO DELETE TABLES EXECUTE:

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
'''

def create_tables():
    db.create_all()

def insert_books():
    f = open("csv-files/booksTest.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
    db.session.commit()

def insert_users():
    f = open("csv-files/usersTest.csv")
    reader = csv.reader(f)
    for name, email, username, password in reader:
        user = User(name=name, email=email, username=username, password=password)
        db.session.add(user)
    db.session.commit()

def insert_reviews():
    f = open("csv-files/reviewsTest.csv")
    reader = csv.reader(f)
    for rating, text, user_id, book_id in reader:
        review = Review(rating= rating, text= text, book_id= book_id, user_id= user_id)
        db.session.add(review)
    db.session.commit()

def check_tables():
    books = Book.query.all()
    users = User.query.all()
    reviews = Review.query.all()

    print("\nBOOKS:")
    for book in books:
        print("BOOK: {} INSERTED SUCCSESSFULLY".format(book.id))
    print("\nUSERS:")
    for user in users:
        print("USER: {} INSERTED SUCCSESSFULLY".format(user.id))
    print("\nREVIEWS:")
    for review in reviews:
        print("REVIEW: {} INSERTED SUCCSESSFULLY".format(review.id))
    print()

def main():
    create_tables()
    insert_books()
    insert_users()
    insert_reviews()
    check_tables()

if __name__ == "__main__":
      # Allows for command line interaction with Flask application

    with app.app_context():
        main()




'''
def delete_tables():
    Book.__table__.drop()
    User.__table__.drop()
    Review.__table__.drop()
    db.commit()
'''
'''
    books = Book.query.all()
    users = User.query.all()
    reviews = Review.query.all()
    for book in books:
        db.session.delete(book)
    for user in users:
        db.session.delete(users)
    for review in reviews:
        db.session.delete(review)
    db.commit()
'''

