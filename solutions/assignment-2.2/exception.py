class InvalidUrl(Exception):

    def __init__(self, msg):
        super(InvalidUrl, self).__init__(msg)
        self.msg = msg
