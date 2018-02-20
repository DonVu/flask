# This is the minitwit web api

import click
from flask import Flask, jsonify
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

#  Read URLs
@app.route('/api/v1/resources/users')
def get_allusers():
    users = query_db('''SELECT * FROM user''')
    return jsonify(users)

@app.route('/api/v1/resources/users/timeline')
def public_timeline():
    timeline = query_db('''SELECT * FROM message''')
    return jsonify(timeline)


#  Errors
@app.errorhandler(404)
def page_not_found(e):
    return jsonify("404 Error"), 404

if __name__=='__main__':
    app.run(debug=true)
