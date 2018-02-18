# This is the minitwit web api

import click
from flask import Flask

app = Flask(__name__)

@app.cli.command('populatedb')
def populatedb_command():
    #Populates the database
    print('Populated the database.');	
