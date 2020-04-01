from typing import Optional
HEADER_END = "\r\n\r\n"
NEW_LINE = "\r\n"


class RequestHeaderBuilder(object):

    def __init__(self):
        super(RequestHeaderBuilder, self).__init__()

    @staticmethod
    def create(url_path='/', request_method='GET', http_version='1.0', **kwargs)-> str:
        request_string_list = []
        request_string_list.append(f"{request_method} {url_path} HTTP/{http_version}")
        for key, val in kwargs.items():
            request_string_list.append(f"{key}: {val}")
        return NEW_LINE.join(request_string_list) + HEADER_END


class ResponseHeaderParser(object):

    def __init__(self, raw_header: str):
        super(ResponseHeaderParser, self).__init__()
        raw_header = raw_header.split(HEADER_END)[0]
        self.request_line, headers = raw_header.split(NEW_LINE, 1)
        self.response_code = self.request_line.split(' ')[1]
        self.header_dict = dict()
        for header in headers.split(NEW_LINE):
            key, value = header.split(": ", 1)
            self.header_dict[key] = value

    def get_filename_from_response(self) -> Optional[str]:
        if 'Content-Disposition' not in self.header_dict:
            return None
        content_disposition = self.header_dict['Content-Disposition']
        if "filename" not in content_disposition:
            return None
        return content_disposition.split('\"')[1]
