import json
import sqlite3
import collections
import logging
import markdown
import multiprocessing as mp
from os.path import abspath, dirname
from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, render_template, jsonify, request, redirect, url_for, Markup
from flask_socketio import SocketIO, emit
from settings import (CONFIG_LOCATION, DATABASE_LOCATION,
                      SCORING_LOG_LOCATION, MARKDOWN_README_LOCATION)

# Stop the flood of messages
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("inotify").setLevel(logging.WARNING)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'securescoring'
socketio = SocketIO(app)

scorine_engine_running = False

scoring_status_thread = None
scoring_status_thread_lock = Lock()
def scoring_status(scoring_process):
    is_alive = scoring_process.is_alive()
    global scorine_engine_running
    while is_alive:
        scorine_engine_running = True
        socketio.sleep(1)
        is_alive = scoring_process.is_alive()
    scorine_engine_running = False
    with scoring_status_thread_lock:
        global scoring_status_thread
        scoring_status_thread = None


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
            config = f.read()
    except Exception as e:
        return render_template('error.html', error=e)
    return render_template('config.html', result=config)


@app.route('/log')
def log():
    return render_template('log.html')


@app.route('/instructions')
def instructions():
    with open(MARKDOWN_README_LOCATION, 'r') as f:
        content = f.read()
    content = Markup(markdown.markdown(content))
    return render_template('instructions.html', md=content)  # TODO: **locals()?


@socketio.on('connect', namespace='/scoring')
def index_connect():
    pass


@socketio.on('start_scoring_engine', namespace='/scoring')
def start_scoring_engine():
    from scoring_engine import scoring_engine_main
    global scoring_process
    scoring_process = mp.Process(target=scoring_engine_main.run_engine)
    scoring_process.start()

    with scoring_status_thread_lock:
        global scoring_status_thread
        if scoring_status_thread is None:
            scoring_status_thread = socketio.start_background_task(scoring_status, scoring_process)


@socketio.on('stop_scoring_engine', namespace='/scoring')
def stop_scoring_engine():
    try:
        scoring_process.terminate()
        logging.info('Scoring Engine was forcibly terminated')

        with scoring_status_thread_lock:
            global scoring_status_thread
            scoring_status_thread = None

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
        try:
            with open(CONFIG_LOCATION, 'w') as f:
                json.dump(
                    json.loads(request.form['json'], object_pairs_hook=collections.OrderedDict),
                    f,
                    indent=4)
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


@app.route('/api/services/uptime')
def uptime():
    services_last_status = {}
    with sqlite3.connect(DATABASE_LOCATION) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_name_response = cursor.fetchall()
            for table in table_name_response:
                table_name = table[0]
                cursor.execute("SELECT * FROM {}".format(table_name))

                # Get the current status
                response = cursor.fetchall()
                last_entry_status = response[-1][2]

                # Get the total time the scoring engine was running
                if len(response) >= 2:
                    start_time = int(response[0][1])
                    stop_time = int(response[-1][1])
                    total_time = stop_time - start_time

                    # Get the uptime
                    total_downtime = 0
                    base = None
                    for result in response:
                        if base is not None:
                            total_downtime += result[1] - base
                            base = None
                        if result[2] == 0:
                            base = result[1]
                    uptime = 100 - (float(total_downtime)/total_time) * 100
                else:
                    if response[0][2] == 1:
                        uptime = 100
                    else:
                        uptime = 0
                services_last_status[table_name] = {
                    'status': last_entry_status,
                    'uptime':"{:.2f}%".format(uptime)
                }
            return jsonify(services_last_status)
        except Exception as e:
            return render_template('error.html', error=e)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
