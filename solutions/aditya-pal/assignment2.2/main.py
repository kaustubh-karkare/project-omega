import argparse
import re
from download import inputs

if __name__ == '__main__':
    arguments = argparse.ArgumentParser()
    arguments.add_argument(
        "-u",
        "--url",
        required=True,
        help="URL of File to be Downloaded"
    )
    arguments.add_argument(
        "-t",
        "--threads",
        default=3,
        required=False,
        help="Number of Threads in which File will be downloaded"
    )
    arguments.add_argument(
        "-p",
        "--port",
        default=80,
        required=False,
        help="Port Number for file download"
    )
    args = arguments.parse_args()
    url_elements = re.split('//', args.url, 1)[-1]
    hostname = re.split('/', url_elements, 1)[0]
    path = re.split('/', url_elements, 1)[-1]
    path = '/' + path
    thread_count = int(args.threads)
    port = int(args.port)
    inputs(hostname, path, port, thread_count)
