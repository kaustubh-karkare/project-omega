import logging


def get_headers(client_socket, parsed_url):
    client_request = (
        'HEAD ' +
        parsed_url.path +
        ' HTTP/1.1\r\n' +
        'Host: ' +
        parsed_url.host +
        '\r\n' +
        'Connection: close' +
        '\r\n\r\n'
    )
    client_socket.send(client_request)
    status, headers_received = client_socket.recv(1024).split('\r\n', 1)
    headers_received = headers_received.splitlines()
    headers = {}
    i = 0
    while i < len(headers_received) - 1:
        current_header = headers_received[i]
        try:
            parameter, value = current_header.split(':', 1)
            headers[parameter] = value[1:]
        except:
            logging.warning(
                'Invalid splitting of header for %s',
                current_header
            )
        i += 1
    return(headers)
