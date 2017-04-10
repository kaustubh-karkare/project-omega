import re
import collections


def parse_url(url):
    pattern = r'(?:[a-z]+:/+)?([a-zA-Z0-9.-]+)?(?::*)?(\d+)?(.*)?'
    url_group = re.match(pattern, url)
    url_tuple = (
        collections.namedtuple(
            'url_tuple',
            'host port path'
        )
    )
    # url_group.group(1) contains host
    # url_group.group(2) contains port
    # url_group.group(3) contains path
    parsed_url = (
        url_tuple(
            url_group.group(1),
            url_group.group(2),
            url_group.group(3),
        )
    )
    return parsed_url
