import socket
import ssl


class URL:

    # https://example.com:8080/path/to/resource
    def __init__(self, url: str) -> None:
        self.host = None
        self.port = None

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "file":
            self.path = url

        else:
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443

            if "/" not in url:
                url = url + "/"
            self.host, url = url.split("/", 1)
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
            self.path = "/" + url

    def request(self, payload: str | None = None) -> str:
        if self.scheme == "file":
            return self.open_file()

        # setup tcp connection
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # send request
        method = "POST" if payload else "GET"
        request = "{} {} HTTP/1.0\r\n".format(method, self.path)
        request += "Host: {}\r\n".format(self.host)
        if payload:  # Content-Length is required for POST requests
            length = len(payload.encode("utf8"))  # length in bytes
            request += "Content-Length: {}\r\n".format(length)
        request += "\r\n"  # end of headers
        if payload:
            request += payload

        s.send(request.encode("utf8"))

        # read response - e.g.: HTTP/1.0 200 OK
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while (line := response.readline()) != "\r\n":
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read()
        s.close()

        return content

    def resolve(self, url: str):
        if "://" in url:
            return URL(url)

        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url

        if self.scheme == "file":
            return URL(self.scheme + "://" + url)
        elif url.startswith("//"):
            return URL(self.scheme + ":" + url)
        else:
            return URL(self.scheme + "://" + self.host +
                       ":" + str(self.port) + url)

    def open_file(self):
        file = open(self.path, "r")
        body = file.read()
        file.close()
        return body

    def __str__(self):
        port_part = ":" + str(self.port) if self.port else ""
        host = self.host if self.host else ""

        if self.scheme == "https" and self.port == 443:
            port_part = ""
        if self.scheme == "http" and self.port == 80:
            port_part = ""
        return self.scheme + "://" + host + port_part + self.path
