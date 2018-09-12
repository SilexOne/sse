import random
from utils.settings import data, collect


@collect(data.get('services').get('random').get('enabled'))
def randomize(config):
    value = bool(random.getrandbits(1))
    if value:
        return 1
    else:
        return 0
