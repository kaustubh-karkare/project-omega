import socket
import threading
import logging
import os


class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.logger = logging.getLogger('Server')
        log_filename = 'Server.log'
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        FileHandler = logging.FileHandler(log_filename)
        self.logger.setLevel(logging.DEBUG)
        FileHandler.setFormatter(formatter)
        self.logger.addHandler(FileHandler)

    def listen(self):
        while True:
            self.socket.listen(2)
            connection, address = self.socket.accept()
            self.logger.info(self.host + ':' + str(self.port))
            function = self.function
            thread = threading.Thread(target=function, args=(connection, address, ))
            thread.start()

    def function(self, connection, address):
        self.logger.info('connection from ' + str(address))
        recieved_data = connection.recv(1024)
        recieved_data = recieved_data.decode().split('\n')[0]
        self.logger.info(recieved_data)
        path = ''
        try:
            path = recieved_data.split(' ')[1]
        except Exception:
            return
        if(path == '/'):
            path = ''
        file_to_check = '.' + path.replace("%20", " ")
        self.logger.info(file_to_check)
        self.logger.info("is a file" + str(os.path.isfile(file_to_check)))
        if os.path.isdir(file_to_check):
            directory_list = os.listdir(path=file_to_check)
            if 'index.html' in directory_list:
                html = open(file_to_check+'/index.html', 'r')
                r = html.read()
            else:
                r = "<html>\n<body>\n"
                for each in directory_list:
                    r += "<a href=" + "'" + path + "/" + each + "'" + ">" + each + "</a><br>\n"
                r += "</body>\n</html>"
            connection.send('HTTP/1.0 200 OK\r\n'.encode())
            connection.send("Content-Type: text/html\r\n".encode())
            header_content_length = "Content-Length: " + str(len(r)) + "\n\n"
            connection.send(header_content_length.encode())
            connection.send(r.encode())
            connection.close()
        elif os.path.isfile(file_to_check):
            file_type = os.path.splitext(path)[-1].lower()
            file_type = file_type[1:len(file_type)]
            size_of_file = os.path.getsize(file_to_check)
            header_content_type = "Content-Type: " + file_type + "\r\n"
            header_content_length = "Content-Length: " + str(size_of_file) + "\n\n"
            self.logger.info(header_content_type + " " + header_content_length)
            connection.send('HTTP/1.0 200 OK\r\n'.encode())
            connection.send(header_content_type.encode())
            connection.send(header_content_length.encode())
            with open(file_to_check, 'rb') as file_to_send:
                read_data = file_to_send.read(1024)
                connection.send(read_data)
                while read_data:
                    read_data = file_to_send.read(1024)
                    connection.send(read_data)
            connection.close()
        else:
            connection.send("HTTP/1.0 404 Not Found\r\n".encode())
            connection.send("Content-Type: text/html\n\n".encode())
            connection.send("<html><body><h1>ERROR 404\nNot Found</h1></body></html>".encode())
            connection.close()


def main():
    server = Server('127.0.0.1', 4000)
    server.listen()


if __name__ == '__main__':
    main()
