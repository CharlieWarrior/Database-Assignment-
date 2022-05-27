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

def is_teacher():
    if session.get("usertype") == "student":
        return False
    return True

def get_categories():
    con = create_connection(DATABASE)
    print(con)
    query = "SELECT id, name FROM categories ORDER BY name ASC"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    return category_list

@app.route('/')
def render_home():
    return render_template("home.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())


@app.route('/category/<catID>')
def render_home1(catID):
    con = create_connection(DATABASE)
    query = "SELECT id, maori_word, english_word, image, level FROM dictionary WHERE cat_id=? ORDER BY maori_word ASC"
    cur = con.cursor()
    cur.execute(query, (catID, ))
    word_list = cur.fetchall()
    con.close()
    return render_template("category.html", logged_in=is_logged_in(), categories=get_categories(), words=word_list, teacher=is_teacher())


@app.route('/word/<ID>')
def render_home2(ID):
    con = create_connection(DATABASE)
    query = "SELECT id, maori_word, english_word, image, definition, editor_id, editted, cat_id FROM dictionary WHERE id=? ORDER BY maori_word ASC"
    cur = con.cursor()
    cur.execute(query, (ID, ))
    word_list = cur.fetchall()
    query = "SELECT * FROM users WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (word_list[0][5], ))
    editor_list = cur.fetchall()

    con.close()
    return render_template("word.html", logged_in=is_logged_in(), categories=get_categories(), word=word_list[0], editor=editor_list[0], teacher=is_teacher())


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if request.method == 'POST':
        print(request.form)
        email = request.form.get('email')
        password = request.form.get('password')

        query = 'SELECT id, fname, usertype FROM users WHERE email=? AND password=?'
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, password))
        user_data = cur.fetchall()
        con.close()

        try:
            user_id = user_data[0][0]
            fname = user_data[0][1]
            user_type = user_data[0][2]
            print(user_id, fname)
        except IndexError:
            return redirect("/login?error=Email+invalid")

        session['email'] = email
        session['userid'] = user_id
        session['fname'] = fname
        session['usertype'] = user_type
        print(session)
        return redirect('/')

    return render_template("login.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        usertype = request.form.get('usertype')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters')

        con = create_connection(DATABASE)

        query = "INSERT INTO users (fname, lname, email, password, usertype) VALUES (?, ?, ?, ?, ?)"

        cur = con.cursor()

        try:
            cur.execute(query, (fname, lname, email, password, usertype))
        except sqlite3.IntegrityError:
            return redirect("/signup?error=Email+already+in+use")

        con.commit()
        con.close()

        return redirect('/login')

    return render_template("signup.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())


@app.route('/logout')
def render_logout():
    session['email'] = None
    return redirect('/login')

@app.route('/addword', methods=['POST', 'GET'])
def render_addword():
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

        con = create_connection(DATABASE)

        query = "INSERT INTO dictionary (id, maori_word, definition, level, english_word, image, cat_id, editted, editor_id) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (maori_word, definition, level, english_word, image, cat_id, editted, editor_id))
        con.commit()
        con.close()

        return redirect('/')
    return render_template("addword.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher())

@app.route('/delete/<cat_id>/<word_id>')
def render_delete(cat_id, word_id):
    return render_template("delete.html", logged_in=is_logged_in(), categories=get_categories(), teacher=is_teacher(),
                           cat_id=cat_id, word_id=word_id)


@app.route('/deleteconfirmed/<cat_id>/<word_id>')
def delete_word(cat_id, word_id):
    con = create_connection(DATABASE)
    query = "DELETE FROM dictionary WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (word_id, ))
    con.commit()
    con.close()

    return redirect("/category/{}".format(cat_id))

if __name__ == '__main__':
    app.run()
