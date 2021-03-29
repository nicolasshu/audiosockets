#%%
import logging

class C:
    def __init__(self):
        pass
args = C()
args.level = "DEBUG"

assert args.level in ["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"]
if args.level == "DEBUG":
    level = logging.DEBUG
elif args.level == "INFO":
    level = logging.INFO
elif args.level == "WARNING":
    level = logging.WARNING
elif args.level == "ERROR":
    level = logging.ERROR
elif args.level == "CRITICAL":
    level = logging.CRITICAL

config = "%(asctime)s - %(message)s"
logging.basicConfig(format=config, level=logging.INFO)

logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
# %%
