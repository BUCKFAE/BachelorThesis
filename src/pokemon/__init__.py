import logging
from datetime import datetime

# Setting up bot_logging
logger = logging.getLogger('pokemon')
extra = {'app_name': 'Bot'}
syslog = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(app_name)s: %(message)s', datefmt='%H:%M:%S')
syslog.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(syslog)


# Logging to file
file_name = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
logger.addHandler(logging.FileHandler(f'src/data/logs/{file_name}.txt'))

logger = logging.LoggerAdapter(logger, extra)
