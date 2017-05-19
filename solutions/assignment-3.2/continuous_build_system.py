import argparse
import json
import logging
import os
import time

from watcher import Watcher


def main():
    logger = logging.getLogger('contiuous_build_system ' + str(time.ctime()))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--cbsconfig',
        '-c',
        required=False,
        default=os.path.join(os.getcwd(), '.cbsconfig'),
        type=str,
        help='Continuous build system(cbs) config file',
    )
    parser.add_argument(
        '--interval',
        '-i',
        required=False,
        default=1,
        type=float,
        help='Interval between consecutive checks',
    )
    parsed_argument = parser.parse_args()
    try:
        with open(parsed_argument.cbsconfig, 'r') as cbsconfig:
            try:
                input_data = json.load(cbsconfig)
                paths_to_watch = input_data.get("watch", os.getcwd())
                action_to_execute = input_data["action"]
            except ValueError:
                logger.error('Key("action") is missing')
                raise
    except IOError:
        logger.error('Continuous build system config file not available')
        raise
    path_watcher = Watcher(
        paths_to_watch,
        action_to_execute,
        logger,
        interval_between_checks=parsed_argument.interval,
    )
    path_watcher.start()
    logger.info('Watcher for path - ' + paths_to_watch + ' started')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        path_watcher.stop_watcher()
        logger.info('KeyboardInterrupt: Watcher stopped:' + paths_to_watch)


if __name__ == '__main__':
    main()
