class InvalidUrl(Exception):
    """Response code for the url is not OK"""

    def __init__(self, msg):
        super(InvalidUrl, self).__init__(msg)
        self.msg = msg
