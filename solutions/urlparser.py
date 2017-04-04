import re
import collections


def parse_url(url):
    pattern = (r'(https?)?(\:\/\/)?([a-zA-Z0-9-.]+)?\:?(\d+)?(.*)')
    url_group = re.match(pattern, url)
    # url_group.group(1) contains protocol
    # url_group.group(3) contains host
    # url_group.group(4) contains port
    # url_group.group(5) contains path
    UrlParser = collections.namedtuple('UrlParser', 'host port path')
    # Default port is 80(Assuming https)
    port = 80
    if url_group.group(4) is not None:
        port = int(url_group.group(4))
    parsed_url = (
        UrlParser(
            url_group.group(3),
            port,
            url_group.group(5)
        )
    )
    return parsed_url
