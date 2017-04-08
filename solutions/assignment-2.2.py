import argparse
import downloadfile


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
        help='Downloaded file name'
    )
    parsed_argument = parser.parse_args()
    downloadfile.DownloadFile(
        url=parsed_argument.url,
        threads=parsed_argument.threads,
        output_path=parsed_argument.output_path
    ).start()

if __name__ == '__main__':
    main()
