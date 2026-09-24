# TODO: Integrate HTTP/2 Support
# TODO: Handle Redirects
# TODO: Read and store cookies
# TODO: Detect password protected websites

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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if use_tls:
        context = ssl.create_default_context()
        context.set_alpn_protocols(["http/1.1"])
        s = context.wrap_socket(s, server_hostname=host)
    
    s.connect((host, port))
    proto = s.selected_alpn_protocol()
    print(f"Protocol Selected: {proto}")
    return s

def send_http_request(s: socket, request, host):

    request = (
        f"GET {request} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    
    # send request

    print("//////////////////////HEADER//////////////////////\n\n")
    print(request)
    s.sendall(request.encode())

def recieve_response(sock: socket):
    response = b""
    # get response
    while True:
        data = sock.recv(4096)
        if not data:
            break;
        response += data
    # print(body.decode
    sock.close()
    return response

def parse_response(response: str) -> str:
    header_data = {}
    header_data["Cookies:"] = []
    header, _, body = response.partition(b"\r\n\r\n")
    header: str = header.decode("ISO-8859-1")
    print(header)
    for line in header.splitlines():
        data = line.split()
        match data[0]:
            case "HTTP/1.1":
                header_data["http_version"] = data[0]
                header_data["status"] = int(data[1])
            case "Location:":
                header_data["redirect"] = data[1]
            case "Set-Cookie:" if header_data["status"] is not 301 or 302:
                cookie_data = ""
                for i in range(1, len(data)):
                    cookie_data += data[i]
                header_data["Cookies:"].append(cookie_data)
    print(header_data)
    # print(header)
    return header
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

    send_http_request(s, uri_data["filepath"], uri_data["host"])

    parse_response(recieve_response(s))
if __name__ == "__main__":
    main()