import sys
import logging
from utils.settings import data

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
logging.basicConfig(format=formatting, level=level)
