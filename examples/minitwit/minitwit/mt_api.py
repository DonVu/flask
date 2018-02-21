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

# Create URLs
@app.route('/api/v1.0/resources/users/register', methods=['POST'])
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

    return jsonify("its success"), 201
    #return jsonify({'mt':entry}), 201

@app.route('/api/v1.0/resources/messages/add', methods=['POST'])
def add_message():
     """Registers a new message for the user."""
     if not request.json or not 'author_id' in request.json or not 'text' in request.json:
         abort(401)

     db = get_db()

     author_id = request.json.get('author_id')
     text = request.json.get('text')
     pub_date =int(time.time())
     db.execute('''insert into message (author_id, text, pub_date) values (?, ?, ?)''',
                (author_id, text, pub_date))
     db.commit()
     return jsonify("message stored: sucess"), 201 

# Delete URLs


@app.route('/api/v1.0/resources/users/delete', methods=['POST'])
def delete_user():
  
    if not request.json or not 'username' in request.json:
        abort(400)

    db = get_db()
    usernameVariable = request.json.get('username')

    db.execute('''DELETE FROM user WHERE username = "{}"'''.format(usernameVariable))
    db.commit()

    return jsonify("Delete is successful"), 201


 #  Errors
@app.errorhandler(404)
def page_not_found(e):
    return jsonify("404 Error Not Found"), 404

if __name__=='__main__':
    app.run(debug=true)
