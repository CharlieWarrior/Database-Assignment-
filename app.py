# This program creates a webpage of a maori dictionary, where users can browse, add or delete words, and login

# Imports the the needed libraries
from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from datetime import datetime

# creates flask instance
app = Flask(__name__)

# This creates a constant variable for the database
DATABASE = "dictionary.db"

# Sets the secret key
app.secret_key = 'abcdefh1234567'


# This function creates a database connection to a SQLite database
def create_connection(db_file):
    # This tries the connection, but if there is no connection, it will return nothing
    try:
        connection = sqlite3.connect(db_file)
        return connection

    except Error as e:
        print(e)

    return None


# This function detects if the user is signed in or not, returning a true or false statement
def is_logged_in():
    # If there is no session for email, it will return False, meaning the entire function id False
    if session.get("email") is None:
        print('Not Logged In')
        return False

    print('Logged In')
    return True


# This function detects if the user is a teacher, returning a True or False statement
def is_teacher():
    # If the session's usertype is student and not teacher, it wil return False
    if session.get("usertype") == "student":
        return False

    return True


# This function selects the id's and name's from the categories database, and orders them in alphabetical order
def get_categories():
    # Creates a connection to the database
    con = create_connection(DATABASE)
    print(con)

    # Requests a query that selects the id and name's from categories and orders them by names alphabetically
    query = "SELECT id, name FROM categories ORDER BY name ASC"
    cur = con.cursor()

    # It then executes this query
    cur.execute(query)

    # It fetches all this data from the query and puts it in the variable category_list
    category_list = cur.fetchall()

    # It then closes the connection to the database
    con.close()

    return category_list


# This function runs when the user is on the home page
@app.route('/')
def render_home():
    # It returns and renders home.html and all the other functions that are constant throughout the program
    return render_template("home.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())


# This function runs when the user is on the page for a category
@app.route('/category/<catID>')
def render_home1(catID):
    # It creates a connection to the database
    con = create_connection(DATABASE)

    # It then requests a query that selects all the relevant information from the dictionary database, from the category
    # that was selected
    query = "SELECT id, maori_word, english_word, image, level FROM dictionary WHERE cat_id=? ORDER BY maori_word ASC"
    cur = con.cursor()

    # It then executes this query
    cur.execute(query, (catID,))

    # It fetches all this data from the query and puts it in the variable word_list
    word_list = cur.fetchall()

    # It then closes the connection to the database
    con.close()

    # It returns and renders category.html and all the other functions that are constant throughout the program
    return render_template("category.html", logged_in=is_logged_in(), categories=get_categories(), words=word_list,
                           teacher=is_teacher())


# This function runs when the user is on the page for a word
@app.route('/word/<ID>')
def render_home2(ID):
    # It creates a connection to the database
    con = create_connection(DATABASE)

    # It then requests query that selects all the relevant details needed for word.html from the dictionary database
    # It knows what word to get as the word id is passed through from category.html
    query = "SELECT id, maori_word, english_word, image, definition, editor_id, editted, cat_id FROM dictionary" \
            " WHERE id=? ORDER BY maori_word ASC"
    cur = con.cursor()

    # It then executes this query
    cur.execute(query, (ID,))

    # It fetches all this data from the database and puts it in the variable word_list
    word_list = cur.fetchall()

    # It also requests a query that selects all the fields available in the users database
    query = "SELECT * FROM users WHERE id=?"
    cur = con.cursor()

    # It then executes this query
    cur.execute(query, (word_list[0][5],))

    # It fetches all the data from the query and puts it in the variable editor_list
    editor_list = cur.fetchall()

    # It then closes the connection with the database
    con.close()

    # It returns and renders word.html and all the other functions that are constant throughout the program
    return render_template("word.html", logged_in=is_logged_in(), categories=get_categories(), word=word_list[0],
                           editor=editor_list[0], teacher=is_teacher())


# This function runs when the user is on the login page
@app.route('/login', methods=['POST', 'GET'])
def render_login():
    # It requests all the information the user input into login.html
    if request.method == 'POST':
        print(request.form)
        email = request.form.get('email')
        password = request.form.get('password')

        # it then requests a query selecting the matching id, firstname, and usertype to the login information input.
        # It requests this from the users database
        query = 'SELECT id, fname, usertype FROM users WHERE email=? AND password=?'

        # It creates a connection to the database
        con = create_connection(DATABASE)
        cur = con.cursor()

        # The query is executed
        cur.execute(query, (email, password))

        # All the data from the query is fetched and stored in the variable user_data
        user_data = cur.fetchall()

        # The connection to the database is then closerd
        con.close()

        # Here, the function tries to see if the queried information matches the login information
        try:
            user_id = user_data[0][0]
            fname = user_data[0][1]
            user_type = user_data[0][2]
            print(user_id, fname)

        # If it doesn't, it returns a redirect to display an error to the user
        except IndexError:
            return redirect("/login?error=Email+invalid")

        # It then stores the session of the relevant information in variables
        session['email'] = email
        session['userid'] = user_id
        session['fname'] = fname
        session['usertype'] = user_type
        print(session)

        # Once logged in, it will redirect you back to the home page
        return redirect('/')

    # It returns and renders login.html and the functions that are constant throughout the program
    return render_template("login.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())


# This function runs when the user is on the signup page
@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    # It requests all the data the user input into signup.html
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        usertype = request.form.get('usertype')

        # If the passwords don't match, it will redirect the user letting them know about the error
        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        # If the password is less then 8 characters, it will redirect the user letting them know about the error
        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters')

        # This creates a connection to the database
        con = create_connection(DATABASE)

        # A query is requested to insert all the information just gathered into the users database
        query = "INSERT INTO users (fname, lname, email, password, usertype) VALUES (?, ?, ?, ?, ?)"

        cur = con.cursor()

        # This function executes the query and check if the user is already in the users database
        try:
            cur.execute(query, (fname, lname, email, password, usertype))

        # If they are, it will redirect the user letting them know about the error
        except sqlite3.IntegrityError:
            return redirect("/signup?error=Email+already+in+use")

        con.commit()

        # The connection to the database is then closed
        con.close()

        # The function then redirects to the login page so the user can login with their new account
        return redirect('/login')

    # It returns and renders signup.html and  the functions that are constant throughout the program
    return render_template("signup.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())


# This function runs when the user is on the logout page
@app.route('/logout')
def render_logout():
    # When the user clicks logout, the session for email is equal to None as they no longer want to be signed in
    session['email'] = None

    # It then redirects to the login page with the user now logged out
    return redirect('/login')


# This function runs when the user is on the add word page
@app.route('/addword', methods=['POST', 'GET'])
def render_addword():
    # It requests all the information the user input on addword.html
    if request.method == 'POST':
        print(request.form)

        maori_word = request.form.get('mword').lower().strip()
        definition = request.form.get('dword').lower().strip()
        level = request.form.get('ylevel')
        english_word = request.form.get('eword').lower().strip()
        image = 'noimage.png'
        cat_id = request.form.get('category')
        editor_id = session['userid']
        editted = datetime.now()

        # A connection to the database is created
        con = create_connection(DATABASE)

        # A query is requested to insert the information the user just input into the dictionary database
        query = "INSERT INTO dictionary (id, maori_word, definition, level, english_word, image, cat_id, editted," \
                " editor_id) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur = con.cursor()

        # The query is then executed
        cur.execute(query, (maori_word, definition, level, english_word, image, cat_id, editted, editor_id))
        con.commit()

        # The connection to the database is then closed
        con.close()

        # It then redirects you to the home page
        return redirect('/')

    # The function returns and renders addword.html and the functions that are constant throughout the program
    return render_template("addword.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())


# This runs when the wants to delete a word
@app.route('/delete/<cat_id>/<word_id>')
def render_delete(cat_id, word_id):
    # The function returns and renders delete.html and the functions that are constant throughout the program
    return render_template("delete.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher(),
                           cat_id=cat_id, word_id=word_id)


# This function runs when the user has confirmed they want to delete a word. cat_id and word_id are passed through from
# delete.html
@app.route('/deleteconfirmed/<cat_id>/<word_id>')
def delete_word(cat_id, word_id):
    # A connection to the database is created
    con = create_connection(DATABASE)

    # A query is request to delete the word and its information from the dictionary database
    query = "DELETE FROM dictionary WHERE id=?"
    cur = con.cursor()

    # The query is then executed
    cur.execute(query, (word_id,))
    con.commit()

    # The connection to the database is then closed
    con.close()

    # The function then redirects you to the category where the deleted word used to be
    return redirect("/category/{}".format(cat_id))


# This code runs the application
if __name__ == '__main__':
    app.run()
