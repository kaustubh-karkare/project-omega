import argparse
import os
import time

from server import Server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, help='Server host')
    parser.add_argument('--port', type=int, default=80, help='Server port')
    parser.add_argument('--document-root', default=os.getcwd())
    parsed_argument = parser.parse_args()
    server = Server(
        parsed_argument.host,
        parsed_argument.port,
        parsed_argument.document_root,
    )
    server.start_serving()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop_serving()


if __name__ == '__main__':
    main()
