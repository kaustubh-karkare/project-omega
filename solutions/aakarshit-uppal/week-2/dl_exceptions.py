"""Exceptions for downloader."""


class NoFileException(Exception):
    def __init__(self):
        error_message = 'Error: Nothing to download.'
        super().__init__(error_message)


class ConnectionException(Exception):
    def __init__(self):
        error_message = 'Error: Unable to connect to download link'
        super().__init__(error_message)


class InvalidLinkException(Exception):
    def __init__(self):
        error_message = 'Error: Invalid link, Nothing to download'
        super().__init__(error_message)
