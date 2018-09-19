import json
import time
import threading
from datetime import datetime, timedelta
from .database import sse_db
from .utils.sse_logging import logging
from .utils.settings import scoring, data
from settings import CONFIG_LOCATION
# The 'from . import services' calls the __init__.py in services and imports
# everything in the directory which runs the decorators to collect all
# the functions
from . import services


def run_engine():
    logging.info("Service Scoring Engine started")

    # Using the json configuration settings from the global variable
    # get the time frame in which the scoring engine will run
    scoring_duration = data.get("timeframe")

    # Initialize a custom object and check if there is another database
    # then create a sqlite3 database
    database = sse_db.SqliteDatabase(__name__)
    database.check_previous()
    database.db_connection()

    # Initialize all the tables in the database
    for service in scoring:
        database.init_table(service.__name__.upper())

    # Get the finish time of the scoring test
    finish_time = datetime.now() + timedelta(hours=int(scoring_duration.get("hours")),
                                             minutes=int(scoring_duration.get("minutes")))

    # Once the database is initialized and the tables have been created
    # we are now able to test the services until the finish time.
    # Since some test can range in test duration it's best
    # to have all the services on their own thread.
    threads = []
    for service in scoring:
        thread = threading.Thread(target=test_service,
                                  name=service.__name__,
                                  args=(finish_time, service))
        thread.start()
        threads.append(thread)

    # Wait till they all finish
    for thread in threads:
        thread.join()

    # Once the appropriate amount of time has elapsed close the
    # connection to the database
    database.close_db()
    logging.info("Service Scoring Engine has finished")


def get_config():
    # Get the contents from the main.json which will act as the config file
    config = json.load(open(CONFIG_LOCATION))
    return config


def test_service(finish_time, service):
    database = sse_db.SqliteDatabase(service.__name__.upper())
    database.db_connection()
    while datetime.now() < finish_time:
        config = get_config()
        try:
            database.commit_to_sqlite(service.__name__.upper(), service(config))
        except Exception as e:
            # Insert a 2 which will cause the scoreboard to display a Blue LED
            # indicating a bad functional service test
            database.commit_to_sqlite(service.__name__.upper(), 2)
            logging.exception("Service test function {} failed: "
                              "{}".format(service.__name__, e))
        time.sleep(5)
    database.close_db()
