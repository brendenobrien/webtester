# Must be able to do the following:
# Confirm whether or not the web server support https
# Cookie name, expiry time (if any), domain name (in any) of cookies that the web server will use
# Whether or not the requested web page is password-protected

# First accept URI from stdin and process it.
# Connect to the server
# Send an HTTP request, and recieve an HTTP response
# Print the response from the server, marking the header and body.
import socket, ssl, sys

def parse_uri(uri: str) -> dict:
    # Grab protocol
    protocol, uri = uri.split("://", 1)
    # grab host, port and filepath
    hostport, filepath = uri.split("/", 1)
    filepath = "/" + filepath
    # if port is included in uri
    if ":" in hostport:
        host, port = hostport.split(":", 1)
    # if port is not in uri
    else:
        host = hostport
        port = "80" if protocol == "http" else "443" if protocol == "https" else ""
    return {"protocol":protocol, "host":host, "port":int(port), "filepath":filepath}
 
def open_connection(host: str, port: int, use_tls=False) -> socket:
    # context = ssl.create_default_context()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if use_tls:
        context = ssl.create_default_context()
        s = context.wrap_socket(s, server_hostname=host)
        
    s.connect((host, port))

    return s

def send_http_request(s: socket, request):
    msg = f"GET {request} HTTP/1.0 \r\n\r\n ".encode()
    # send request
    s.send(msg)

def recieve_response(sock: socket):
    response = b""
    # get response
    while True:
        data = sock.recv(4096)
        if not data:
            break;
        response += data
    header, _, body = response.partition(b"\r\n\r\n")
    print(header.decode())
    sock.close()
    return response

def parse_response(response):
    pass;
def handle_redirects():
    pass;
def check_http2_support():
    pass;
def extract_cookies(headers):
    pass;
def check_password_protection(status_code):
    pass;

def main():
    if len(sys.argv) == 1:
        raise ValueError("Must provide web server.");
    uri_data = parse_uri(sys.argv[1])
    print(uri_data)
    if uri_data["protocol"] == "https":
        s = open_connection(uri_data["host"], uri_data["port"], True)
    elif uri_data["protocol"] == "http":
        s = open_connection(uri_data["host"], uri_data["port"])
    send_http_request(s, uri_data["filepath"])
    recieve_response(s)
if __name__ == "__main__":
    main()