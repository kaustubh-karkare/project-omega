import logging


class DefaultLogger:
    LOGGER_INSTANCE = None

    @staticmethod
    def get_instance():
        if DefaultLogger.LOGGER_INSTANCE:
            return DefaultLogger.LOGGER_INSTANCE
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        debug_handler = logging.StreamHandler()
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt="%H:%M:%S"))
        logger.addHandler(debug_handler)
        error_handler = logging.StreamHandler()
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(
            logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S"))
        logger.addHandler(error_handler)
        DefaultLogger.LOGGER_INSTANCE = logger
        return DefaultLogger.LOGGER_INSTANCE