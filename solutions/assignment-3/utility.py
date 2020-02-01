import re

def compute_request_ranges(headers, parts):
    '''
    Calculates ranges to download the resource according to
    number of parts specified
    '''
    if "Accept-Ranges" not in headers:
        raise KeyError("Server does not accept range requests")

    data_ranges = list()
    start = 0
    file_size = int(headers["Content-Length"])
    part_size = int(file_size / parts)
    iters = parts - 1 if file_size % parts != 0 else parts

    for _ in range(iters):
        data_ranges.append(str(start) + "-" + str(start+part_size-1))
        start += part_size
    if start < file_size:
        data_ranges.append(str(start) + "-" + str(file_size-1))
    return data_ranges

def get_headers(socket):
    '''
    Received header data
    '''
    response_msg = ''
    msg_buffer = socket.recv(1)
    response_msg += msg_buffer.decode()
    while response_msg[-4:] != '\r\n\r\n':
        msg_buffer = socket.recv(1)
        response_msg += msg_buffer.decode()
    return response_msg

def parse_header_data(header_data, expected_resp_code):
    headers = header_data.strip().split('\r\n')
    http_version, resp_code, resp_status_msg = headers.pop(0).split(" ", 2)
    assert (resp_code == expected_resp_code), 'Expected %s HTTP response code, got %s.\nResponse Status Message: %s\n' % (expected_resp_code, resp_code, resp_status_msg)
    assert (http_version == 'HTTP/1.1')
    parsed_headers = dict()
    for header_line in headers:
        header, data = header_line.split(': ')
        parsed_headers[header] = data
    return parsed_headers

def download_payload(socket, save_as, content_length):
    download_length = 0

    with open(save_as, 'wb') as download_file:
        while download_length < content_length:
            packet = socket.recv(content_length - download_length)
            if not packet:
                return None
            download_length += len(packet)
            download_file.write(packet)

def generate_request(req_method, resource, server_addr, data_range=None):
    request_line = "%s /%s HTTP/1.1\r\n" % (req_method, resource)

    if data_range is not None:
        data_range = "bytes=" + data_range
    header_dict = {
        'User-Agent': 'Python Script',
        'Host': '%s' % (server_addr),
        'Accept': '*/*',
        'Range': data_range
    }
    request = (request_line + "".join("%s: %s\r\n" % (key, value) for key, value in header_dict.items() if value is not None) + "\r\n")
    return request


def find_server_and_resouce(url):
    '''
    Finds server, port and resorce path from url using regex

    regex_pattern -
        non-capturing group 1 : http protocol
        capturing group 1: host
        non-capturing group 2: colon(:)
        capturing group 2: port number
        non-capturing group 3: slash(/) - unnecessary will rectify it later
        capturing group 3: path to resource
    '''
    regex_pattern = '^(?:http:\/\/)([^:\/?]+)(?:[\:]?)([0-9]*)(?:\/?)(.*)$'
    pattern_obj = re.compile(regex_pattern)
    assert (url.partition('://')[0] == 'http'), "Error! Script can only work for HTTP based servers."
    host, port, resource = pattern_obj.findall(url)[0]

    port = int(port) if port else 80 #assign default TCP port 80 if none assigned
    resource = '/' if not resource else resource

    return host, port, resource
