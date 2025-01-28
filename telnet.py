#This is our own implementation of `telnet` to parse the requests on the browser and return its response
import socket

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        # Creating a socket connection
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        ) # Creating a socket to connect with other computers
        s.connect((self.host, 80)) # Connecting to the host on Port 80 (host is the site we want to communicate, eg- google.com)

        # Requesting the data. Next 3 lines is equivalent to
        # GET /index.html HTTP/1.0
        # Host: example.org
        #
        # This is how we get the index.html content in telnet, we are doing something very similar here.
        request = "GET {} HTTP/1.0\r\n".format(self.path) #\r - Carriage return, takes the pointer to the first character
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        # Send the Created Command
        s.send(request.encode("utf8"))
        # Read the response received and create a file out of it
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read()
        s.close()
        return content


def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))