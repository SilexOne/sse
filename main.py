import os
import sys
import json
import sqlite3
from subprocess import Popen
from flatten_json import flatten_json, unflatten
from flask import Flask, render_template, jsonify, request, redirect, url_for
from settings import CONFIG_LOCATION, PYTHON_ENV, SCORING_ENGINE_LOCATION, DATABASE_LOCATION

import logging
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # Not to flood the terminal messages
app = Flask(__name__)


@app.route('/')
def scoreboard():
    # TODO: Display timer
    # TODO: Indicate end of scoring
    # TODO: Update scoreboard, scoreboard still there when db is gone
    return render_template("index.html")


@app.route('/config')
def config():
    config = read_config().json
    return render_template('config.html', result=config)


@app.route('/api/config', methods=['POST', 'GET'])
def read_config():
    if request.method == 'GET':
        try:
            with open(CONFIG_LOCATION, 'r') as f:
                config = json.load(f)
        except Exception as e:
            return str(e)
        flat_json = [{'name': k, 'value': v} for k, v in flatten_json(config).items()]
        return jsonify(flat_json)
    elif request.method == 'POST':
        result = request.form
        result = unflatten(result)
        with open(CONFIG_LOCATION, 'w') as f:
            json.dump(result, f, indent=4)

        return redirect(url_for('scoreboard'))


@app.route('/api/engine', methods=['POST', 'GET'])
def start_scoring_engine():
    if request.method == 'POST':
        # TODO: Once running gray out option, enable a terminate button
        # TODO: Use a database to store the boolean buttons enabled/disabled or pass it?
        # TODO: Importing is crazy??? Help!
        scoring_engine = Popen([PYTHON_ENV, SCORING_ENGINE_LOCATION],
                                stdout=sys.stdout, stderr=sys.stderr, env=os.environ)
        return redirect(url_for('scoreboard'))
    elif request.method == 'GET':
        return ''


@app.route('/api/services/status')
def score_board():
    services_last_status = {}
    with sqlite3.connect(DATABASE_LOCATION) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_name_response = cursor.fetchall()
            for table in table_name_response:
                table_name = table[0]
                cursor.execute("SELECT * FROM {} ORDER BY id DESC LIMIT 1".format(table_name))
                last_entry_response = cursor.fetchone()
                last_entry_status = last_entry_response[2]
                services_last_status[table_name] = last_entry_status
            return jsonify(services_last_status)
        except Exception as e:
            return str(e)


@app.route('/api/tables')
def list_tables():
    tables = []
    with sqlite3.connect(DATABASE_LOCATION) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        response = cursor.fetchall()
        for table in response:
            tables.append(table[0])
        return str(tables)


@app.route('/api/tables/<tablename>')
def query_table(tablename):
    response = ''
    with sqlite3.connect(DATABASE_LOCATION) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM {}".format(tablename))
            all_rows = cursor.fetchall()
            for row in all_rows:
                response += '{0} | {1} | {2}<br/>'.format(row[0], row[1], row[2])
            return str(response)
        except Exception as e:
            return str(e)


@app.route('/api/tables/last/<tablename>')
def query_table_last_entry(tablename):
    with sqlite3.connect(DATABASE_LOCATION) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM {}".format(tablename))
            all_rows = cursor.fetchall()
            last_entry = '{0} | {1} | {2}'.format(all_rows[-1][0], all_rows[-1][1], all_rows[-1][2])
            return str(last_entry)
        except Exception as e:
            return str(e)


if __name__ == '__main__':
    app.run()
