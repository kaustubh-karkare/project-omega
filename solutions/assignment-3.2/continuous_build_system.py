import argparse
import json
import logging
import os
import time

from buildutility import BuildUtility


def main():
    logging.info('Logger for continuous_build_system')
    logger = logging.getLogger('contiuous_build_system' + str(time.ctime()))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configfile',
        '-f',
        required=False,
        default=os.path.join(os.getcwd(), '.configfile'),
        type=str,
        help='Config file'
    )
    parsed_argument = parser.parse_args()
    try:
        with open(parsed_argument.configfile, 'r') as configfile:
            try:
                input_data = json.load(configfile)
                watch = input_data["watch"]
                action = input_data["action"]
            except ValueError:
                logger.error('Key("watch"/"action") is missing')
                raise
    except IOError:
        logger.error('Config file not available')
        raise
    BuildUtility(watch, action).start()


if __name__ == '__main__':
    main()
