import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_logger(name):
    setup_logging()
    return logging.getLogger(name)
