import socket
from urllib.parse import urlparse

LE = "\r\n"
CRLF = "\r\n\r\n"


def GET(url):
    url = urlparse(url)
    path = url.path
    if path == "":
        path = "/"
    HOST = url.netloc
    PORT = 80
    socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_object.connect((HOST, PORT))
    header_request = "HEAD " + path + " HTTP/1.1" + LE
    header_request += "Host: " + HOST + CRLF
    socket_object.send(header_request.encode())
    header = (socket_object.recv(1024)).decode()
    content_length = 0
    for each in header.split('\n'):
        if ':' in each and 'Content-Length' in each:
            x = each.split(':')
            content_length = x[1][1:]
    get_request = "GET " + path + " HTTP/1.1" + LE
    get_request += "Host: " + HOST + CRLF
    socket_object.send(get_request.encode())
    recieved_data = (socket_object.recv(4096)).decode()
    while(len(recieved_data) < int(content_length)):
        recieved_data += (socket_object.recv(4096)).decode()
    file = open("somefile", 'w')
    file.write(recieved_data)
    file.close()
    socket_object.shutdown(1)
    socket_object.close()


GET('http://www.daisuki.net/anime.html#')
