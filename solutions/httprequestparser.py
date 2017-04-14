import re
from collections import namedtuple


def parse_http_request(http_request):
    request_line, separator, received_headers = (
        http_request.partition(
            '\r\n'
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
    header_pattern = (r'([A-Za-z-]+)\:\s+(.*)?')
    received_headers = received_headers.splitlines()
    for line in received_headers:
        if not line:
            break
        header_group = re.match(header_pattern, line)
        headers[header_group.group(1)] = header_group.group(2)
    return (http_request_data, headers)
