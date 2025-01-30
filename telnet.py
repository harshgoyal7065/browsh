#This is our own implementation of `telnet` to parse the requests on the browser and return its response
import socket
import ssl
import tkinter
import sys

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        # Creating a socket connection
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        ) # Creating a socket to connect with other computers
        s.connect((self.host, self.port)) # Connecting to the host on Port 80/ self port (host is the site we want to communicate, eg- google.com)
        # Making an encrypted connection with ssl is pretty easy.
        # Suppose you’ve already created a socket, s, and connected it to example.org.
        # To encrypt the connection, you use ssl.create_default_context to create a context ctx and use that context to wrap the socket s:
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

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
        statusline = response.readline() # First line of response is status line, reading status line
        version, status, explanation = statusline.split(" ", 2)
        # For the headers, I split each line at the first colon and fill in a map of header names to header values.
        # Headers are case-insensitive, so I normalize them to lower case.
        # I used casefold instead of lower, because it works better for more languages.
        # Whitespace is insignificant in HTTP header values, so I strip off extra whitespace at the beginning and end.
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        # If header transfer-encoding or content-encoding is present, data is is unusual form and can't be read.
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read()
        s.close()
        return content

WIDTH, HEIGHT = 800, 600

def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text
class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()

    def load(self, url):
        body = url.request()
        text = lex(body)
        HSTEP, VSTEP = 13, 18
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in text:
            self.canvas.create_text(cursor_x, cursor_y, text=c)
            cursor_x += HSTEP
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP

if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()