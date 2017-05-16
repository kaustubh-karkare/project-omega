import argparse
import json
import logging
import os
import time

from watcher import Watcher


def main():
    logging.info('Logger for continuous_build_system(cbs)')
    logger = logging.getLogger('contiuous_build_system' + str(time.ctime()))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--cbsconfig',
        '-f',
        required=False,
        default=os.path.join(os.getcwd(), 'cbsconfig'),
        type=str,
        help='Continuous build system(cbs) config file'
    )
    parsed_argument = parser.parse_args()
    try:
        with open(parsed_argument.cbsconfig, 'r') as cbsconfig:
            try:
                input_data = json.load(cbsconfig)
                paths_to_watch = input_data.get("watch")
                action_to_execute = input_data["action"]
            except ValueError:
                logger.error('Key("action") is missing')
                raise
    except IOError:
        logger.error('Continuous build system config file not available')
        raise
    if paths_to_watch is None:
        paths_to_watch = os.getcwd()
    path_watcher = Watcher(paths_to_watch, action_to_execute)
    path_watcher.start()
    time.sleep(30)
    path_watcher.stop_watcher()


if __name__ == '__main__':
    main()
