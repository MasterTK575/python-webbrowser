import socket
from urllib import parse


def handle_connection(conx: socket.socket):
    req = conx.makefile("b")
    reqline = req.readline().decode('utf8')
    method, url, version = reqline.split(" ", 2)
    assert method in ["GET", "POST"]

    headers = {}
    while True:
        line = req.readline().decode('utf8')
        if line == '\r\n':
            break
        header, value = line.split(":", 1)
        headers[header.casefold()] = value.strip()

    if 'content-length' in headers:
        length = int(headers['content-length'])
        body = req.read(length).decode('utf8')
    else:
        body = None

    status, body = do_request(method, url, headers, body)
    response = "HTTP/1.0 {}\r\n".format(status)
    response += "Content-Length: {}\r\n".format(
        len(body.encode("utf8")))
    response += "\r\n" + body
    conx.send(response.encode('utf8'))
    conx.close()


ENTRIES = ['Pavel was here']


def do_request(method, url, headers, body) -> tuple[str, str]:
    if method == "GET" and url == "/":
        return "200 OK", show_comments()
    elif method == "GET" and url == "/comment.js":
        with open("comment.js") as f:
            return "200 OK", f.read()
    elif method == "GET" and url == "/comment.css":
        with open("comment.css") as f:
            return "200 OK", f.read()
    elif method == "POST" and url == "/add":
        params = form_decode(body)
        return "200 OK", add_entry(params)
    else:
        return "404 Not Found", not_found(url, method)


def show_comments() -> str:
    out = "<!doctype html>"
    out += "<script src=/comment.js></script>"
    out += "<link rel=stylesheet href=/comment.css></link>"

    for entry in ENTRIES:
        out += "<p>" + entry + "</p>"

    out += "<form action=add method=post>"
    out += "<p><input name=guest></p>"
    out += "<strong></strong>"
    out += "<p><button>Sign the book!</button></p>"
    out += "</form>"

    return out


def form_decode(body) -> dict:
    params = {}
    for field in body.split("&"):
        name, value = field.split("=", 1)
        name = parse.unquote_plus(name)
        value = parse.unquote_plus(value)
        params[name.casefold()] = value
    return params


def add_entry(params: dict) -> str:
    if 'guest' in params and len(params['guest']) <= 10:  # our input field has name=guest
        ENTRIES.append(params['guest'])
    return show_comments()


def not_found(url, method) -> str:
    out = "<!doctype html>"
    out += "<h1>{} {} not found!</h1>".format(method, url)
    return out


if __name__ == "__main__":
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 8000))
    s.listen()

    while True:
        conx, addr = s.accept()
        print("Received connection from", addr)
        handle_connection(conx)
