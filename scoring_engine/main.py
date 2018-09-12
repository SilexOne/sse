import os
import json
import time
from datetime import datetime, timedelta
from database import sse_db
from utils.sse_logging import logging
from utils.settings import scoring, data
from settings import CONFIG_LOCATION
# This 'import services' calls the __init__.py in services and imports
# everything in the directory which runs the decorators to collect all
# the functions
import services


def main():
    logging.info("Service Scoring Engine started")

    # Using the json configuration settings from the global variable
    # get the time frame in which the scoring engine will run
    scoring_duration = data.get("timeframe")

    # Initialize a sqlite3 database
    database = sse_db.SqliteDatabase()

    # Initialize all the tables in the database
    for service in scoring:
        database.init_table(service.__name__.upper())

    # Get the finish time of the scoring test
    finish_time = datetime.now() + timedelta(hours=int(scoring_duration.get("hours")),
                                             minutes=int(scoring_duration.get("minutes")))

    # Once the database is initialized and the tables have been created
    # we are now able to test the services until the finish time
    while datetime.now() < finish_time:
        config = get_config()
        for service in scoring:
            try:
                database.commit_to_sqlite(service.__name__.upper(), service(config))
            except Exception as e:
                logging.exception("Service test function {} failed: "
                                  "{}".format(service.__name__, e))
        time.sleep(5)  # TODO: Find better way

    # Once the appropriate amount of time has elapsed close the
    # connection to the database
    # TODO: Indicate end of scoring
    database.close_db()
    logging.info("Service Scoring Engine has finished")


def get_config():
    # Get the contents from the main.json which will act as the config file
    config = json.load(open(os.path.join(os.path.dirname(__file__), CONFIG_LOCATION)))
    return config


if __name__ == '__main__':
    main()
