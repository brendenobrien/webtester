# TODO: Integrate HTTP/2 Support
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
        s = context.wrap_socket(s, server_hostname=host)
    
    s.connect((host, port))
    # check_http2_support(s)
    return s

def send_http_request(s: socket, path, host):
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n\r\n"
    )
    # send request
    print(request)
    s.sendall(request.encode())

def receive_response(sock: socket):
    response = b""
    # get response
    while True:
        data = sock.recv(4096)
        if not data:
            break;
        response += data
    # print(body.decode)
    sock.close()
    return response

def parse_response(response: str) -> dict:
    header_data = {}
    header_data["cookies"] = []
    header, _, body = response.partition(b"\r\n\r\n")
    header: str = header.decode("ISO-8859-1")
    #print(header)
    lines = header.splitlines()
    version_status_line = lines[0].split()
    header_data["http_version"] = version_status_line[0]
    header_data["status"] = version_status_line[1]
    for line in lines[1:]:
        name, value = line.split(":", 1)
        value = value.strip()
        if name == "Location":
            header_data["redirect"] = value
        elif name == "Set-Cookie" and header_data["status"] not in (301, 302):
            header_data["cookies"].append(value)
    print(header_data)
    print(header)
    print()
    return header_data

def handle_redirects(location: str) -> dict:
    uri_data = parse_uri(location)
    s = open_connection(uri_data["host"], uri_data["port"], True)
    send_http_request(s, uri_data["filepath"], uri_data["host"])
    header_data = parse_response(receive_response(s))
    if not "redirect" in header_data:
        return header_data
    else:
        return handle_redirects(header_data["redirect"])

def check_http2_support(socket: ssl.SSLSocket):
    proto = socket.selected_alpn_protocol()
    print(f"Protocol Selected: {proto}")
    return

def extract_cookies(cookies: list) -> list:
    extracted_cookies = []
    for i in cookies:
        cookie_data = {}
        # print(i)
        chunks = i.strip().split(";")
        cookie_data["name"] = chunks[0].split("=")[0]
        for j in chunks[1:]:
            key, _, value = j.partition("=")
            key = key.strip()
            if key == "expires":
                # print("test")
                cookie_data["expires"] = value
            elif key == "domain":
                # print("test2")
                cookie_data["domain"] = value

        extracted_cookies.append(cookie_data)
        print(cookie_data)
    return extracted_cookies

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

    header_data = parse_response(receive_response(s))
    if "redirect" in header_data:
        header_data = handle_redirects(header_data["redirect"])
    extract_cookies(header_data["cookies"])
    
if __name__ == "__main__":
    main()