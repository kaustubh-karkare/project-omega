import re
import datetime
from time import sleep

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

def get_headers(sock):
    '''
    Receive header data from socket
    '''
    response_msg = ''
    msg_buffer = sock.recv(1)
    response_msg += msg_buffer.decode()
    while response_msg[-4:] != '\r\n\r\n':
        msg_buffer = sock.recv(1)
        response_msg += msg_buffer.decode()
    return response_msg

def parse_response(response_data, expected_resp_code):
    headers = response_data.strip().split('\r\n')
    http_version, resp_code, resp_status_msg = headers.pop(0).split(" ", 2)
    assert (resp_code == expected_resp_code), 'Expected %s HTTP response code, got %s.\nResponse Status Message: %s\n' % (expected_resp_code, resp_code, resp_status_msg)
    assert (http_version == 'HTTP/1.1')
    parsed_headers = dict()
    for header_line in headers:
        header, data = header_line.split(': ')
        parsed_headers[header] = data
    return parsed_headers

def parse_request(request_data):
    headers = request_data.strip().split('\r\n')
    req_method, resource,  http_version = headers.pop(0).split()
    assert (http_version == 'HTTP/1.1')
    recv_headers = dict()
    for header_line in headers:
        header, data = header_line.split(': ')
        recv_headers[header] = data
    return (req_method, resource, http_version, recv_headers)

def download_payload(socket, save_as, content_length):
    download_length = 0

    with open(save_as, 'wb') as download_file:
        while download_length < content_length:
            packet = socket.recv(content_length - download_length)
            if not packet:
                return None
            download_length += len(packet)
            download_file.write(packet)

def send_data_chunks(sock, chunk_size, file_handler, seek_start, seek_end):
    file_handler.seek(seek_start)
    while file_handler.tell() <= seek_end:
        data_chunk = file_handler.read(chunk_size)
        if not data_chunk:
            break
        sock.sendall(data_chunk)
        sleep(1)
    file_handler.close()

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

def generate_response(total_content_length, resp_status_msg, content_range=None):
    response_line = 'HTTP/1.1 %s\r\n' % (resp_status_msg)
    time_now = datetime.datetime.now()
    if content_range is not None:
        a, b = map(int, content_range.split('-'))
        content_length = b-a
        content_range = 'bytes %s/%s' %  (content_range, total_content_length)
    else:
        content_length = total_content_length
    send_headers = { 'Server' : 'Python Script',
                     'Content-Length' : content_length,
                     'Content-Range' : content_range,
                     'Accept-Ranges' : 'bytes',
                     'Date' : time_now.strftime("%d %b %Y, %H:%M:%S GMT") }
    send_data = ''.join("%s: %s\r\n" % (key, value) for key, value in send_headers.items() if value is not None)

    return response_line + send_data + '\r\n'

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
