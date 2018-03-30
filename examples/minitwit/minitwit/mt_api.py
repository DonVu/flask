# This is the minitwit web api

import click
from flask import Flask, jsonify, request, abort, _app_ctx_stack
from sqlite3 import dbapi2 as sqlite3
#from minitwit import *
from flask_basicauth import BasicAuth

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'password'



# Overriding BasicAuth

class ApiAuth(BasicAuth):
    def check_credentials(self, username, password): 
         username_exists = query_db("SELECT pw_hash FROM user WHERE username = ?", [username])       

         if (username_exists):
             print "User found"
             username_password =  username_exists[0]["pw_hash"]
             return password == username_password
    
         print "User not found"
         return False

user_auth = ApiAuth(app)
basic_auth = BasicAuth(app)

# database configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30

#databse functions from minitwit.py
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                 for idx, value in enumerate(row))

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(DATABASE)
        top.sqlite_db.row_factory = make_dicts
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def query_db(query, args= (), one=False):
     """Queries the database and returns a list of dictionaries."""
     cur = get_db().execute(query, args)
     rv = cur.fetchall()
     return (rv[0] if rv else None) if one else rv


# --------- end of minitwit.py DB functions-------

def populate_db():
    # Populates the database
    db = get_db()
    with app.open_resource('population.sql', mode = 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def delete_from_db(database_column, database_table):
    if not request.json or not database_column in request.json:
        abort(400)

    db = get_db()
    delete_request = request.json.get(database_column)

    db.execute('DELETE FROM %s WHERE %s = "%s"' % (database_table, database_column, delete_request))
    db.commit()

@app.cli.command('populatedb')
def populatedb_command():
    #Populates the database
    populate_db()
    print('Populated the database.')



#  Read URLs
@app.route('/api/v1.0/resources/users', methods=['GET'])
@basic_auth.required
def get_allusers():
    users = query_db('''SELECT * FROM user''')
    return jsonify(users)



@app.route('/api/v1.0/resources/users/timeline', methods=['GET'])
def public_timeline():
    timeline = query_db('''SELECT message.*, user.* FROM message, user
                           WHERE message.author_id = user.user_id
                           order by message.pub_date desc limit ?''', [PER_PAGE])
    return jsonify(timeline)



# get user id by username
@app.route('/api/v1.0/resources/users/<username>', methods=['GET'])
def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                 [username], one=True)

    return jsonify(rv[0]) if rv else None

# the timeline is accessed by the front end passing in the user's id
@app.route('/api/v1.0/resources/users/timeline/<user_id>', methods=['GET'])
def timeline(user_id):
    result = query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id and (
            user.user_id = ? or
            user.user_id in (select whom_id from follower
                                    where who_id = ?))
        order by message.pub_date desc limit ?''', [user_id, user_id, PER_PAGE])
    return jsonify(result)

# get user record by user id
@app.route('/api/v1.0/resources/users/uid/<user_id>', methods=['GET'])
def get_user_record(user_id):
    result = query_db('select * from user where user_id = ?',
                          user_id, one=True)
    return jsonify(result)

# user records may be accessed by username



@app.route('/api/v1.0/resources/users/<username>/following', methods=['GET'])
@user_auth.required
def users_following(username):
    query = '''SELECT user_id FROM user WHERE username = "{}"'''.format(username)
    result = query_db(query)
    userID_dict = result[0]
    uID = userID_dict['user_id']

    query2 = '''SELECT whom_id FROM follower WHERE who_id = "{}"'''.format(uID)
    result2 = query_db(query2)
    
    print(result2)

    followers = []
    for following_dict in result2:
        whom_id = following_dict['whom_id']
        query3 = '''SELECT username FROM user WHERE user_id = "{}"'''.format(whom_id)
        result3 = query_db(query3)
        followers.append(result3)
   
    print(followers) 
    return jsonify(followers)



@app.route('/api/v1.0/resources/users/<username>/timeline', methods=['GET'])
def user_timeline(username):
    query = '''SELECT user_id FROM user WHERE username = "{}"'''.format(username)
    result = query_db(query)
    userID_dict = result[0]
    uID = userID_dict['user_id']

    query2 = '''SELECT whom_id FROM follower WHERE who_id = "{}"'''.format(uID)
    result2 = query_db(query2)

    messages = []
    for following_dict in result2:
        whom_id = following_dict['whom_id']
        query3 = '''SELECT text FROM message WHERE author_id = "{}"'''.format(whom_id)
        result3 = query_db(query3)
        messages.append(result3)

    return jsonify(messages)



# Create URLs
@app.route('/api/v1.0/resources/users/', methods=['POST'])
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



@app.route('/api/v1.0/resources/messages/', methods=['POST'])
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
     return jsonify("message stored: sucessessful"), 201 



# Delete URLs
@app.route('/api/v1.0/resources/users/', methods=['DELETE'])
def delete_user():
    db_column = 'username'
    db_table = 'user'
    delete_from_db(db_column, db_table)
    
    return jsonify("Delete user is successful"), 201



@app.route('/api/v1.0/resources/messages/', methods=['DELETE'])
def delete_message():
    db_column = 'message_id'
    db_table = 'message'
    delete_from_db(db_column, db_table) 

    return jsonify("Delete message is successful"), 201



 #  Errors
@app.errorhandler(400)
def bad_request(e):
    return jsonify("400 Bad Request"), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify("401 Unauthorized"), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify("403 Forbidden"), 403

@app.errorhandler(404)
def page_not_found(e):
    return jsonify("404 Error Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify("500 Internal Server Error"), 500

if __name__=='__main__':
    app.run(debug=true)
