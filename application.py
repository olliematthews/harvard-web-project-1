import os

from flask import Flask, session, render_template, request, session
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

# Make sure every user is logged route
db.execute("UPDATE users SET logged_in = False")
db.commit()

@app.route("/")
def index():
    return render_template("login.html", messages=[])

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        '''check login details'''
        username = request.form.get('usrnm')
        password = request.form.get('pwd')
        if db.execute("SELECT * FROM users WHERE (username = :usrnm) AND (password = :pwd)", {"usrnm": username, "pwd": password}).rowcount == 0:
            message = {'fail' : True,
                    'message' : 'There is no account with this username and password.'}
            return render_template("login.html", messages = [message])
        else:
            entry = db.execute("SELECT * FROM users WHERE (username = :usrnm) AND (password = :pwd)", {"usrnm": username, "pwd": password}).fetchone()
            if not entry.logged_in:
                user_id = entry.id
                db.execute("UPDATE users SET logged_in = True where id = :id", {'id' : user_id})
                db.commit()
                session['user_id'] = user_id
                return render_template("search.html", logged_in = True)
            else:
                message = {'fail' : True,
                        'message' : 'Someone is already logged in with this username.'}
                return render_template("login.html", messages = [message])
    elif not session.get('user_id') is None:
        return render_template("search.html", logged_in = True)
    else:
        return render_template("login.html", messages = [])

@app.route("/signup", methods=["POST", "GET"])
def signup():
    '''check login details'''
    if request.method == 'POST':
        username = request.form.get('usrnm')
        password = request.form.get('pwd')
        cpassword = request.form.get('cpwd')
        if not password == cpassword:
            message = {'fail' : True,
                    'message' : 'Passwords do not match.'}
            return render_template("signup.html", messages = [message])

        if not db.execute("SELECT * FROM users WHERE username = :usrnm", {'usrnm' : username}).rowcount == 0:
            message = {'fail' : True,
                    'message' : 'Username already exists.'}
            return render_template("signup.html", messages=[message])

        else:
            '''Create user'''
            print(username, password)
            db.execute("INSERT INTO users (username, password, logged_in) VALUES (:usrnm, :pwd, False)",
                        {'usrnm' : username, 'pwd' : password})
            db.commit()
            message = {'fail' : False,
                    'message' : 'Account created. Log in here.'}
            return render_template("login.html", messages = [message])

    else:
        return render_template("signup.html", messages=[])

@app.route("/signout")
def signout():
    try:
        db.execute("UPDATE users SET logged_in = False where id = :id", {'id' : session['user_id']})
        db.commit()
        session.pop('user_id')
    except KeyError:
        pass
    message = {'fail' : False,
                'message' : 'Successfully logged out'}
    return render_template("login.html", messages = [message])

@app.route("/search")
def search():
    return render_template("search.html", logged_in = not session.get('user_id') is None)

@app.route("/search_results", methods=["POST"])
def search_results():
    search = request.form.get('search')
    try:
        search_number = int(search)
    except ValueError:
        search_number = None

    search_results = db.execute("SELECT * FROM books WHERE (lower(isbn) LIKE lower(:search)) OR (lower(title) LIKE lower(:search)) OR (lower(author) LIKE lower(:search)) OR (year = :number)",
    {'search' : '%' + search + '%', 'number' : search_number}).fetchall()
    return render_template("search_results.html", logged_in = not session.get('user_id') is None, search_results = search_results)

@app.route("/book_summaries/<int:book_id>")
def book_summary(book_id):
    """Lists details about a book."""
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    return render_template("book_summary.html", book=book)
