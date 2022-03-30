from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from datetime import datetime

app = Flask(__name__)
DATABASE = "smile.db"

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None

@app.route('/')
def render_home():
    return render_template("home.html")

@app.route('/animals')
def render_menu():
    return render_template("animals.html")

if __name__ == '__main__':
    app.run()
