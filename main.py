import json
import sqlite3
import logging
import multiprocessing as mp
from os.path import abspath, dirname
from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
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

scoring_status_thread = None
scoring_status_thread_lock = Lock()
def scoring_status(scoring_process):
    is_alive = scoring_process.is_alive()
    while is_alive:
        socketio.sleep(1)
        is_alive = scoring_process.is_alive()


class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('scoring.log'):
            try:
                with open(SCORING_LOG_LOCATION, 'r') as f:
                    log_file = f.read()
                    socketio.emit('message', log_file, namespace='/status')
            except Exception as e:
                socketio.emit('message', e, namespace='/status')
            socketio.sleep(1)


log_thread = None
log_thread_lock = Lock()
def log_status():
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, dirname(abspath(__file__)))
    observer.start()
    try:
        while True:
            socketio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


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


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


@socketio.on('start_scoring_engine', namespace='/scoring')
def start_scoring_engine():
    from scoring_engine import scoring_engine_main
    global scoring_process
    scoring_process = mp.Process(target=scoring_engine_main.run_engine)
    scoring_process.start()
    global scoring_status_thread
    with scoring_status_thread_lock:
        if scoring_status_thread is None:
            scoring_status_thread = socketio.start_background_task(scoring_status, scoring_process)


@socketio.on('stop_scoring_engine', namespace='/scoring')
def stop_scoring_engine():
    try:
        scoring_process.terminate()
        with scoring_status_thread_lock:
            scoring_status_thread = None
        logging.info('Scoring Engine was forcibly terminated')
    except NameError:
        logging.warning('No Scoring Engine Process found')
    except Exception:
        logging.exception('Scoring Engine was unable to be forcibly terminated')

@socketio.on('connect', namespace='/status')
def connect():
    try:
        with open(SCORING_LOG_LOCATION, 'r') as f:
            log_file = f.read()
            emit('init', log_file)
    except Exception as e:
        emit('init', e)
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
