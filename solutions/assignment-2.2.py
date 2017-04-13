import argparse
from filedownloader import FileDownloader


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL to download'
    )
    parser.add_argument(
        '--threads',
        type=int,
        required=False,
        default=4,
        help='Number of threads to download'
    )
    parser.add_argument(
        '--output-path',
        '-o',
        type=str,
        required=True,
        help='Downloaded output file name'
    )
    parsed_options = parser.parse_args()
    FileDownloader(
        url=parsed_options.url,
        threads=parsed_options.threads,
        output_path=parsed_options.output_path,
    ).start()

if __name__ == '__main__':
    main()
