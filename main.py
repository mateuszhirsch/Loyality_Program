import random
import threading
import json
import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# create the application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY = 'development key',
    USERNAME = 'admin',
    PASSWORD = 'default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent = True)

# Function whitch add every minute default number of points (0-10) by first 30 minutes afters creating new coustumer
def add_points():
    db = get_db()
    cur = db.execute('SELECT last_insert_rowid()')
    row = cur.fetchone()[0]
    for i in range(30):
        threading.Timer((i+1)*60, add_default_points,[row]).start()
    return

def add_default_points(row):
    with app.app_context():
        db = get_db()
        #FUP Add some if statment to check if record wasn't deleted
        cur = db.execute('select points from customers where id=?', [row])
        points = cur.fetchone()[0]
        points = points+random.randrange(10)
        db.execute('update customers set points=? where id=?', [points,row])
        db.commit()
        return

# Connects to the database
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

# Opens a new database connection if there is none yet for the current application context
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()

# Initializes the database
#FUP Doesn't work ivestigate why!!!
@app.cli.command('initdb')
def initdb_command():
    init_db()
    print 'Initialized the database.'


# Closes the database again at the end of the request
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# Returns list of all customers and their data
@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, name, last_name, date_of_birth, points from customers')
    entries = cur.fetchall()
    # Code to make encode JSON data
    # dict = {}
    # all_querry = []
    # for query in db.execute('select id, name, last_name, date_of_birth, points from customers'):
    #     dict = {
    #         'id' : query[0],
    #         'name' : query[1],
    #         'last_name' : query[2],
    #         'date_of_birth' : query[3]
    #     }
    #     all_querry.append(dict)
    # entries = json.dumps(all_querry)
    # print(entries)
    return render_template('show_entries.html', entries=entries)


# Adds new record to the database
@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into customers (name, last_name, date_of_birth, points) values (?, ?, ?, 0)', [request.form['name'], request.form['last_name'], request.form['date_of_birth']])
    db.commit()
    flash('New entry was successfully posted')
    add_points();
    return redirect(url_for('show_entries'))

# Delets a record from the database
@app.route('/remove', methods=['POST', 'DELETE'])
def remove_entry():
    db = get_db()
    db.execute('delete from customers where id=(?)', [request.form['id']])
    db.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('show_entries'))

# Modifies a racord in the database
@app.route('/modify', methods=['POST', 'PUT'])
def modify_entry():
    db = get_db()
    db.execute('update customers set name=?, last_name=?, date_of_birth=? where id=?', [request.form['name'], request.form['last_name'], request.form['date_of_birth'], request.form['id']])
    db.commit()
    flash('Entry was successfully modified')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(debug=True)
