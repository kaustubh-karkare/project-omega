import re
from exception import InvalidUrl
from typing import Optional

URL_PATTERN = re.compile("^(.*://)?([A-Za-z0-9\-\.]+)(:[0-9]+)?(.*)$")


class UrlParser(object):

    def __init__(self, url):
        super(UrlParser, self).__init__()
        url_data = re.match(URL_PATTERN, url)
        try:
            self.scheme = url_data.groups()[0][: -3]
        except TypeError:
            raise InvalidUrl(f'url scheme is missing in {url}')
        self.host = url_data.groups()[1]
        self.port = int(url_data.groups()[2][1:]) if url_data.groups()[2] else 80 if self.scheme == 'http' else 443
        self.path_with_query = url_data.groups()[3] if url_data.groups()[3] else "/"

    def get_filename_from_url(self)-> Optional[str]:
        path = self.path_with_query.split('?')[0]
        if path == '/':
            return None
        return path.split('/')[-1]
