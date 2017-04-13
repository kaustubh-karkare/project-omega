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
    url_data = (
        url_tuple(
            protocol=url_group.group(1),
            host=url_group.group(2),
            port=url_group.group(3),
            path=url_group.group(4),
        )
    )
    return url_data
