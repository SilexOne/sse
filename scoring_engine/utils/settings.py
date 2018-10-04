import os
import sys
import json
import logging
from settings import CONFIG_LOCATION
# Create a global variable that can be passed to other
# files so collect can add functions to scoring
scoring = []
# Get the contents from the main.json which will act as the config file
data = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), CONFIG_LOCATION)))


# Make this a decorator on all services so the
# function can be added to the global variable
def collect(enabled):
    def real_decorator(func):
        if not(enabled == True or enabled == False):
            logging.exception("The decorator argument on {} service function must "
                              "be either a 'true' or 'false', check the JSON configuration "
                              "file to ensure that it's correct".format(func.__name__))
            sys.exit(1)
        if enabled == True:
            scoring.append(func)
    return real_decorator
