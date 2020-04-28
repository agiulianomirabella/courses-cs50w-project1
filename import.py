import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

os.environ['DATABASE_URL'] = 'postgresql://wfwoewdbugkurk:85896f0531941d15a43b9b864b47376882347a56b7d19161fb044850141b8ebe@ec2-54-217-204-34.eu-west-1.compute.amazonaws.com:5432/d2ldkrsktl45l4'
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def delete_tables():
    db.execute("DROP SCHEMA public CASCADE;")
    db.execute("CREATE SCHEMA public;")
    db.execute("GRANT ALL ON SCHEMA public TO postgres;")
    db.execute("GRANT ALL ON SCHEMA public TO public;")
    db.commit()

def create_tables():
    db.execute(
        "CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL);"
    )
    db.execute(
        "CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, email VARCHAR NOT NULL, username VARCHAR NOT NULL, password INTEGER NOT NULL);"
    )
    db.execute(
        "CREATE TABLE reviews (id SERIAL PRIMARY KEY, rating INTEGER NOT NULL, text VARCHAR NOT NULL, user_id INTEGER REFERENCES users, book_id INTEGER REFERENCES books);"
    )
    db.commit()

def insert_books():
    f = open("csv-files/booksTest.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute(
            "INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn":isbn, "title":title, "author":author, "year":year}
        )
    db.commit()

def insert_users():
    f = open("csv-files/usersTest.csv")
    reader = csv.reader(f)
    for name, email, username, password in reader:
        db.execute(
            "INSERT INTO users (name, email, username, password) VALUES (:name, :email, :username, :password)",
            {"name":name, "email":email, "username":username, "password":password}
        )
    db.commit()

def insert_reviews():
    f = open("csv-files/reviewsTest.csv")
    reader = csv.reader(f)
    for rating, text, user_id, book_id in reader:
        db.execute(
            "INSERT INTO reviews (rating, text, user_id, book_id) VALUES (:rating, :text, :user_id, :book_id)",
            {"rating":rating, "text":text, "user_id":user_id, "book_id":book_id}
        )
    db.commit()

def check_tables():
    books = db.execute("SELECT * FROM books").fetchall()
    users = db.execute("SELECT * FROM users").fetchall()
    reviews = db.execute("SELECT * FROM reviews").fetchall()

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
    delete_tables()
    create_tables()
    insert_books()
    insert_users()
    insert_reviews()
    check_tables()

if __name__ == "__main__":
    main()

