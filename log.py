import logging
import sys

formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S %p')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handlerStd = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handlerStd.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(handlerStd)

    return logger