import re
import collections


def parse_url(url):
    pattern = r'(?:([a-z]+)?(?::/+))?([a-zA-Z0-9.-]+)?(?::*)?(\d+)?(.*)?'
    url_group = re.match(pattern, url)
    url_tuple = (
        collections.namedtuple(
            'url_tuple',
            ['protocol', 'host', 'port', 'path']
        )
    )
    server_port = None
    if url_group.group(3) is not None:
        server_port = int(url_group.group(3))
    url_data = (
        url_tuple(
            protocol=url_group.group(1),
            host=url_group.group(2),
            port=server_port,
            path=url_group.group(4),
        )
    )
    return url_data
