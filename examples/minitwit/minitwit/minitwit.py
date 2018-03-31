# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""

import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
import requests

# configuration
API_BASE_URL = "http://localhost:5001"
PER_PAGE = 30
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# create our little application :)
app = Flask('minitwit')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    response = requests.get(API_BASE_URL + "/api/v1.0/resources/\"{}\"".format(username))
    rv = response.json()
    return rv.text if rv else None

def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = requests.get(API_BASE_URL + "/api/v1.0/resources/users/uid/{}"
                               .format(session['user_id']))


@app.route('/')
def timeline():
    '''Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    '''
    if not g.user:
        return redirect(url_for('public_timeline'))

    response = requests.get(API_BASE_URL + '/api/v1.0/resources/users/timeline/{0}' 
                             .format(session['user_id']))

    return render_template('timeline.html', messages=response.json())



@app.route('/public')
def public_timeline():
    '''Displays the latest messages of all users.'''
    response = requests.get(API_BASE_URL + '/api/v1.0/resources/users/timeline')

    return render_template('timeline.html', messages=response.json())



@app.route('/<username>')
def user_timeline(username):
    '''Display's a users tweets.'''
    profile_user  =  requests.get(API_BASE_URL + 
                               '/api/v1.0/resources/users/usernames/{}'
                                .format(username)).json()

    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        payload = {'session': session['user_id'],
                   'profile_user': profile_user['user_id']}
        followed =  requests.get(API_BASE_URL +
                                  '/api/v1.0/resources/users/followed',
                                  params=payload).json() is not None

    payload2 = {'profile_user': profile_user['user_id']}
    messages = requests.get(API_BASE_URL + '/api/v1.0/resources/messages',
                             params=payload2).json()
    return render_template('timeline.html', messages=messages, followed=followed,
            profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    '''Adds the current user as follower of the given user.'''
    if not g.user:
        abort(401)
    response = requests.get(API_BASE_URL + '/api/v1.0/resources/users/usernames/{}'
                            .format(username)).json()
    whom_id = response['user_id']
    
    if whom_id is None:
        abort(404)
    requests.post(API_BASE_URL + '/api/v1.0/resources/users/follow',
                   data = {'whom_id': whom_id,
                           'session': session['user_id']})
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    '''Removes the current user as follower of the given user.'''
    if not g.user:
        abort(401)
    response = requests.get(API_BASE_URL + '/api/v1.0/resources/users/usernames/{}'
                            .format(username)).json()
    whom_id = response['user_id']
    if whom_id is None:
        abort(404)
    
    requests.delete(API_BASE_URL + '/api/v1.0/resources/users/unfollow',
                     data = {'whom_id' : whom_id,
                             'session' : session['user_id']})
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    '''Registers a new message for the user.'''
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        requests.post(API_BASE_URL + '/api/v1.0/resources/messages/',
                       data = {'session'  : session['user_id'],
                               'text'     : request.form['text'],
                               'post_time': int(time.time())})
        flash('Your message was recorded')
    return redirect(url_for('timeline'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Logs the user in.'''
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = requests.get(API_BASE_URL + 
                '/api/v1.0/resources/users/usernames/{}' \
                  .format(request.form['username'])).json()
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''Registers the user.'''
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif requests.get(API_BASE_URL + '/api/v1.0/resources/users/{}' \
                          .format(request.form['username'])).json() \
                         is not None:
            error = 'The username is already taken'
        else:
            requests.post(API_BASE_URL + '/api/v1.0/resources/users/', 
                           data = {'username': request.form['username'],
                                   'email'   : request.form['email'],
                                   'password': generate_password_hash(
                                               request.form['password'])})
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
