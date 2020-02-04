import socket
import os
import io
import select
import threading
import utility


class FileServer:
    """
    Creates a server which sends requested resource. If request
    is a directory then server sends existing index.html file else
    generates a list of files and directories and sends that.
    If the request is for a file, server sends that.

    :param interface: ip address where the server will Host
    :param port: port number to host server as
    :param logger: logger object used for debugging and other running information
    :param server_location: system path to run server at
    :param speed_limit_bps: speed limit in bytes per second to send data
    """

    def __init__(self, interface, port, logger, server_location, speed_limit_bps):
        self.interface = interface
        self.port = port
        self.homepage = 'http://' + interface + ':' + str(port)
        self.server_location = server_location
        os.chdir(self.server_location)
        self.logger = logger
        self.speed_limit_bps = speed_limit_bps
        self.run = False

    def start(self):
        """
        Create socket instance and bind ip address and host
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.interface, self.port))
        self.logger.info("Server started")
        self.run = True
        self._handle_request()

    def stop(self, *args):
        #issues with stopping the while loop, stopping process not quite ready yet
        self.logger.info("Exiting")
        self.run = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def _handle_request(self):
        """
        Handles incoming request in non-blocking way
        """
        self.sock.listen(10)
        read_list = [self.sock]

        while self.run:
            read_ready, write_ready, execption_list = select.select(read_list, [], [])
            for sock in read_ready:
                if sock is self.sock:
                    self.logger.info('Listening at %s' % (self.homepage))
                    conn_obj, client_addr = self.sock.accept()
                    read_list.append(conn_obj)
                    self.logger.info("Accepted connection from %s" % (client_addr,))
                else:
                    # make threads and send back requested resource
                    req_handler = RequestHandler(sock, self.__dict__)
                    req_thread = threading.Thread(target=req_handler.run())
                    req_thread.start()
                    req_thread.join()
                    read_list.remove(sock)


class RequestHandler:
    """
    Processes request and sends back requested data

    :param conn_obj: accepted connection
    :param server_info: information about server
    """

    def __init__(self, conn_obj, server_info):
        self.conn_obj = conn_obj
        self.server_info = server_info
        self.logger = server_info['logger']

    def run(self):
        self.logger.info("Receiving headers")
        request_received = utility.get_headers(self.conn_obj)
        self.logger.debug("Headers received: \n%s" % (request_received))
        self.req_method, self.resource, http_ver, self.recv_headers = utility.parse_request(request_received)
        self._process_request()
        self.logger.info("Request processed")
        self.conn_obj.close()
        self.logger.info("Closing socket")

    def _process_request(self):
        content_length = None
        resp_status_msg = '200 OK'
        content_range = None
        resource = self.resource.strip('/')
        path = os.path.join(self.server_info['server_location'], resource)

        if 'Range' in self.recv_headers:
            content_range = self.recv_headers['Range'].strip('bytes=')
            seek_start, seek_end = map(int, content_range.split('-'))
            resp_status_msg = '206 Partial Content'
        else:
            seek_start, seek_end = 0, None

        if os.path.isdir(path):
            index_path = os.path.join(path, 'index.html')
            if os.path.exists(index_path):
                upload_file = open(index_path, 'rb')
                self.logger.info("Sending index.html")
                content_length = os.stat(index_path).st_size
            else:
                self.logger.info("Generating directory listing and sending")
                upload_file = io.BytesIO()
                list_page = self._generate_index_of('/' +  resource)
                content_length = len(list_page)
                upload_file.write(list_page.encode())

        elif os.path.isfile(resource):
            if os.path.exists(path):
                upload_file = open(path, 'rb')
                self.logger.info("Sending requested file")
                content_length = os.stat(path).st_size
            else:
                self.logger.info("Requested file not found, sending error response")
                resp_status_msg = '404 Not Found'

        else:
            self.logger.info("Requested resource not found")
            resp_status_msg = '404 Not Found'


        resp_headers = utility.generate_response(content_length, resp_status_msg, content_range)
        self.logger.debug("Sending headers:\n%s" % (resp_headers))
        self.conn_obj.sendall(resp_headers.encode())

        if self.req_method == "GET" and resp_status_msg != '404 Not Found':
            if seek_end is None:
                utility.send_data_chunks(self.conn_obj, self.server_info['speed_limit_bps'], upload_file, seek_start, content_length-1)
            else:
                utility.send_data_chunks(self.conn_obj, self.server_info['speed_limit_bps'], upload_file, seek_start, seek_end)

    def _generate_index_of(self, location):

        head_template = ('<html>\n'
                         '<head>\n'
                         '<title>Directory listing for %s</title>\n'
                         '</head>\n' % (self.resource))

        all_lists = []
        for content in os.listdir('.' + location):
            link = os.path.join(self.server_info['homepage'], self.resource, content)
            listing = '<li><a href=%s>%s</a></li>\n' % (link, content)
            all_lists.append(listing)
        all_lists = ''.join(all_lists)

        body_template = ('<body>\n'
                         '<h1>Directory listing for %s</h1>\n'
                         '<hr>\n'
                         '<ul>\n'
                         '%s'
                         '</ul>\n'
                         '<hr>\n'
                         '</body>\n'
                         '</html>' % (self.resource, all_lists))

        return head_template + body_template
