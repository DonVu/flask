# This is the minitwit web api

import click
from flask import Flask
from sqlite3 import dbapi2 as sqlite3
from minitwit import *

app = Flask(__name__)

def populate_db():
    # Populates the database
    db = get_db()
    with app.open_resource('population.sql', mode = 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('populatedb')
def populatedb_command():
    #Populates the database
    populate_db()
    print('Populated the database.')
