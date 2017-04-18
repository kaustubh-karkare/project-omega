import re
from collections import namedtuple

EOL = '\r\n'


def parse_http_request(http_request):
    request_line, separator, received_headers = (
        http_request.partition(
            EOL
        )
    )
    pattern = (r'([A-Z]+)(?:\s+)(\S+)(?:\s+)(.*)')
    request_line_group = re.match(pattern, request_line)
    request_line_tuple = (
        namedtuple(
            'request_line_tuple',
            ['method', 'path', 'version']
        )
    )
    http_request_data = (
        request_line_tuple(
            method=request_line_group.group(1),
            path=request_line_group.group(2),
            version=request_line_group.group(3),
        )
    )
    headers = {}
    received_headers = received_headers.splitlines()
    for line in received_headers:
        if not line:
            break
        key, separator, value = line.partition(': ')
        headers[value] = key
    return (http_request_data, headers)
