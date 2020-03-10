from server import FileServer
import logging
import argparse
import signal
from os import getcwd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', '-p', type=int, default=8000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--location', default=getcwd())
    parser.add_argument('--speed_limit', type=int, default=256*1000)
    args = parser.parse_args()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logger = logging.getLogger('server_logger')
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    server = FileServer(args.host, args.port, logger, args.location, args.speed_limit)
    signal.signal(signal.SIGINT, server.stop)
    server.start()
