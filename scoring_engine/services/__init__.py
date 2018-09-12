import pkgutil
import logging


__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__ + '.'):
    try:
        __import__(modname)
        logging.info("Imported Service Test: {}".format(modname))
    except AttributeError:
        pass  # The main.json has no reference when @collect is called which is fine
    except Exception as e:
        logging.exception("Unable to import Service Test {}: {}".format(modname, e))
