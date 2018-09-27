import sys
import logging
from .settings import data


# Set the logging settings
formatting = '%(asctime)s [%(levelname)s]: %(message)s'
if data.get('logging') not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    logging.error("Check the JSON configuration logging option. Only options allowed:"
                  "\nDEBUG"
                  "\nINFO"
                  "\nWARNING"
                  "\nERROR"
                  "\nCRITICAL")
    sys.exit(1)
level = logging.getLevelName(data.get('logging'))
# TODO: Make dynamic
file_handler = logging.FileHandler('scoring.log', mode='w')
stdout_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(format=formatting, level=level, handlers=[file_handler, stdout_handler])
