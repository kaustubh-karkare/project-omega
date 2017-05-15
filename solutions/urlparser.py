import re
import collections


UrlTuple = (
    collections.namedtuple(
        'UrlTuple',
        ['protocol', 'host', 'port', 'path']
    )
)


def parse_url(url):
    pattern = r'(?:([a-z]+)?(?::/+))?([a-zA-Z0-9.-]+)?(?::*)?(\d+)?(.*)?'
    url_group = re.match(pattern, url)
    port = None
    if url_group.group(3) is not None:
        port = int(url_group.group(3))
    url_data = (
        UrlTuple(
            protocol=url_group.group(1),
            host=url_group.group(2),
            port=port,
            path=url_group.group(4),
        )
    )
    return url_data
