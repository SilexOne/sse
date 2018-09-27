import sys
import json
import sqlite3
import logging
try:
    pass
    #import inotify.adapters
except AttributeError:
    logging.exception('inotify may only be ran on Linux. Windows and MacOS will not work')
    sys.exit(1)
import multiprocessing as mp
from threading import Lock
from flatten_json import flatten_json, unflatten
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
from settings import CONFIG_LOCATION, DATABASE_LOCATION, SCORING_LOG_LOCATION

# Stop the flood of messages
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("inotify").setLevel(logging.WARNING)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'securescoring'
socketio = SocketIO(app)

log_thread = None
log_thread_lock = Lock()
def log_status():
    count = 0
    while True:
        socketio.sleep(1)
        count += 1
        socketio.emit('test', str(count), namespace='/status')
"""
    i = inotify.adapters.Inotify()
    from os.path import dirname, join
    i.add_watch(join(dirname(__file__), 'status'))
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
              path, filename, type_names))    
        try:
            with open(SCORING_LOG_LOCATION, 'r') as f:
                log_file = f.read()
                emit('message', log_file)
        except Exception as e:
            emit('message', e)
    
"""


@app.route('/')
def scoreboard():
    return render_template("index.html")


@app.route('/config')
def config_display():
    try:
        with open(CONFIG_LOCATION, 'r') as f:
            config = json.load(f)
    except Exception as e:
        return render_template('error.html', error=e)
    try:
        flat_json = [{'name': k, 'value': v} for k, v in flatten_json(config).items()]
        sorted_flat_json = sorted(flat_json, key=lambda k: k['name'])
        config = sorted_flat_json
    except Exception as e:
        return render_template('error.html', error=e)
    return render_template('config.html', result=config)


@app.route('/log')
def log():
    return render_template('log.html')


@socketio.on('connect', namespace='/status')
def connect():
    global log_thread
    with log_thread_lock:
        if log_thread is None:
            log_thread = socketio.start_background_task(target=log_status)


@app.route('/api/config', methods=['POST', 'GET'])
def read_config():
    if request.method == 'GET':
        try:
            with open(CONFIG_LOCATION, 'r') as f:
                config = json.load(f)
        except Exception as e:
            return render_template('error.html', error=e)
        return jsonify(config)
    elif request.method == 'POST':
        result = request.form
        result = unflatten(result)
        try:
            with open(CONFIG_LOCATION, 'w') as f:
                json.dump(result, f, indent=4)
        except Exception as e:
            return render_template('error.html', error=e)

        return redirect(url_for('scoreboard'))


@app.route('/api/engine', methods=['POST', 'GET'])
def start_scoring_engine():
    if request.method == 'POST':
        from scoring_engine import scoring_engine_main
        scoring_process = mp.Process(target=scoring_engine_main.run_engine)
        scoring_process.start()
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
            return render_template('error.html', error=e)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
