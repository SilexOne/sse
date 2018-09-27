import sys
from os.path import join, dirname, abspath
import scoring_engine
from scoring_engine import database

DATABASE_DIR = dirname(database.__file__)
DATABASE_NAME = 'sse.db'
DATABASE_LOCATION = join(DATABASE_DIR, DATABASE_NAME)
CONFIG_DIR = dirname(scoring_engine.__file__)
CONFIG_NAME = 'main.json'
CONFIG_LOCATION = join(CONFIG_DIR, CONFIG_NAME)
PYTHON_ENV = sys.executable
SCORING_ENGINE = 'scoring_engine_main.py'
SCORING_ENGINE_LOCATION = join(CONFIG_DIR, SCORING_ENGINE)
SCORING_LOG_NAME = 'scoring.log'
SCORING_LOG_LOCATION = join(abspath(dirname(__file__)), SCORING_LOG_NAME)
