import argparse
import downloadfile
import concurrent.futures


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
    # Maximum simultaneous downloads is default to 4
    max_simultaneous_download = 4
    executor = (
        concurrent.futures.ThreadPoolExecutor(
            max_workers=max_simultaneous_download
        )
    )
    download_files = []
    download_files.append(
        executor.submit(
            downloadfile.DownloadFile,
            url=parsed_argument.url,
            threads=parsed_argument.threads,
            output_path=parsed_argument.output_path,
        )
    )
    concurrent.futures.wait(download_files)

if __name__ == '__main__':
    main()
