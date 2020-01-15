import socket

class Client():

    def __init__(self, host=None, port=80):
        self.host = host
        self.port = 80

    def connect(self, host, port=80):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, self.port))

    def stop(self):
        self.sock.close()

    def generate_request(self, resource_addr, server_addr):
        GET_request = ("GET /%s HTTP/1.1\r\nHost: %s\r\nAccept: */*\r\n\r\n" % (resource_addr, server_addr)).encode()
        return GET_request

    def send(self, url):
        resource_addr, server_addr = self.find_server_and_resouce(url)
        self.connect(server_addr)
        request = self.generate_request(resource_addr, server_addr)
        self.sock.sendall(request)

    def receive(self    ):
        header_data = self.get_response_headers()
        content_length = self.get_content_length(header_data)
        payload = self.get_payload(content_length)
        self.response_data = {'header_data':header_data, 'payload':payload}

    def get_response_headers(self):
        response_msg = ''
        msg_buffer = self.sock.recv(1)
        response_msg += msg_buffer.decode()
        while response_msg[-4:] != '\r\n\r\n':
            msg_buffer = self.sock.recv(1)
            response_msg += msg_buffer.decode()
        return response_msg

    def get_content_length(self, header_data):
        seek = header_data.find('Content-Length') + 16
        content_length = ''
        while header_data[seek] != '\r':
            content_length += header_data[seek]
            seek += 1
        return int(content_length)

    def get_payload(self, content_length):
        payload = b''
        while len(payload) < content_length:
            packet = self.sock.recv(content_length - len(payload))
            if not packet:
                return None
            payload += packet
        return payload

    def save_file(self):
        with open('download_file', 'wb') as download_file:
            download_file.write(self.response_data['payload'])

    def download(self, url):
        self.send(url)
        self.receive()
        self.save_file()
        self.stop()

    @staticmethod
    def find_server_and_resouce(url):
        server_addr, slash, resource_addr = url.partition('//')[-1].partition('/')
        return resource_addr, server_addr
