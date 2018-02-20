# This is the minitwit web api

import click
from flask import Flask, jsonify, request, abort
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

@app.route('/api/v1/resources/users/<username>/following')
def users_following(username):
    query = '''Select * FROM follower, user WHERE username = "{}"'''.format(username)
    print (query)
    # query = query + "\"" + username + "\""
    result = query_db(query)
    return jsonify(result)

@app.route('/api/v1/resources/user/register?username=<username>&email=<email>&pw_hash=<pw_hash>', methods=['PUT'])
def register_user(username, email, pw_hash):
    print (username)
    print (email)
    print (pw_hash)
    return jsonify('register successful')

@app.route('/api/v1.0/register', methods=['POST'])
def register():
  
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'pw_hash' in request.json:
        abort(400)

    db = get_db()
    entry = {

       'username': request.json.get('username'),
       'email': request.json.get('email'),
       'pw_hash': request.json.get('pw_hash')
    }

    db.execute('''insert into user (
             username, email, pw_hash) values (?, ?, ?)''',(entry['username'], entry['email'],entry['pw_hash']))
    db.commit()

  # return jsonify({'mt':entry}), 201
    return jsonify("its success"), 201

#  Errors
@app.errorhandler(404)
def page_not_found(e):
    return jsonify("404 Error Not Found"), 404

if __name__=='__main__':
    app.run(debug=true)
