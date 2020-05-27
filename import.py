'''
Script to import the information from books and save it to a database called 'books'
'''
import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


filename = 'books.csv'
try:
    db.execute("DROP TABLE books")
except:
    pass
db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY,isbn VARCHAR NOT NULL,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year INTEGER NOT NULL);")
db.commit()
with open(filename) as file:
    reader = csv.reader(file)
    first = True
    for line in reader:
        if first:
            first = False
            continue
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {'isbn' : line[0], 'title' : line[1], 'author' : line[2], 'year' : line[3]})
    db.commit()
