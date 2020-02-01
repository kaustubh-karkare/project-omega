import logging
import argparse
from file_downloader import FileDownloader

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--save_as')
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logger = logging.getLogger('file_downloader_logger')
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    downloader = FileDownloader(args.url, args.save_as, logger, args.threads)
    downloader.start()
    downloader.download()
