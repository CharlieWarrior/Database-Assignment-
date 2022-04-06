from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from datetime import datetime

app = Flask(__name__)
DATABASE = "dictionary.db"
app.secret_key = 'abcdefh1234567'



def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


def is_logged_in():
    if session.get("email") is None:
        print('Not Logged In')
        return False
    print('Logged In')
    return True


@app.route('/')
def render_home():
    return render_template("home.html", logged_in=is_logged_in())


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if request.method == 'POST':
        print(request.form)
        email = request.form.get('email')
        password = request.form.get('password')

        query = 'SELECT id, fname FROM users WHERE email=? AND password=?'
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, password))
        user_data = cur.fetchall()
        con.close()

        try:
            user_id = user_data[0][0]
            fname = user_data[0][1]
            print(user_id, fname)
        except IndexError:
            return redirect("/login?error=Email+invalid")

        session['email'] = email
        session['userid'] = user_id
        session['fname'] = fname
        print(session)
        return redirect('/')

    return render_template("login.html", logged_in=is_logged_in())


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters')

        con = create_connection(DATABASE)

        query = "INSERT INTO users (fname, lname, email, password) VALUES (?, ?, ?, ?)"

        cur = con.cursor()

        # This Line Doesn't Work

        try:
            cur.execute(query, (fname, lname, email, password))
        except sqlite3.IntegrityError:
            return redirect("/signup?error=Email+already+in+use")

        con.commit()
        con.close()

        return redirect('/login')

    return render_template("signup.html", logged_in=is_logged_in())


@app.route('/animals')
def render_menu():
    return render_template("animals.html", logged_in=is_logged_in())


@app.route('/logout')
def render_logout():
    session['email'] = None
    return redirect('/')


if __name__ == '__main__':
    app.run()
