# TODO: Integrate HTTP/2 Support
# TODO: Detect password protected websites
# TODO: Error Handling:
# TODO: Remove hardcoding of "use_tls" in handle_redirects() and handle dynamically

import socket, ssl, sys

def parse_uri(uri: str) -> dict:
    protocol = None
    # Grab protocol
    if "://" in uri:
        protocol, uri = uri.split("://")
    
    # grab host, port and filepath
    hostport, _, filepath = uri.partition("/")
    filepath = "/" + filepath

    # Assigns port if exists, if port doesnt exist then hostport just resolves into host
    host, _, port = hostport.partition(":")
    if port:
        port = int(port)
        if protocol is None:
            protocol = "https" if port == 443 else "http" if port == 80 else ""
    else:
        if protocol is None:
            protocol = "https"
        port = 80 if protocol == "http" else 443

    return {"protocol":protocol, "host":host, "port":port, "filepath":filepath}
 
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
        f"Connection: close\r\n"
        f"\r\n"
    )
    # send request
    print("~~~ Request ~~~")
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
    sock.close()
    return response

def parse_response(response: str) -> dict:
    header_data = {}
    header_data["cookies"] = []
    header, _, body = response.partition(b"\r\n\r\n")
    header: str = header.decode("ISO-8859-1")
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
    # print(header_data)
    print("~~~ Response Header ~~~")
    print(header)
    print()
    return header_data

def handle_redirects(location: str, use_tls: bool) -> dict:
    uri_data = parse_uri(location)
    s = open_connection(uri_data["host"], uri_data["port"], use_tls)
    send_http_request(s, uri_data["filepath"], uri_data["host"])
    header_data = parse_response(receive_response(s))
    header_data["host"] = uri_data["host"]
    if not "redirect" in header_data:
        return header_data
    else:
        return handle_redirects(header_data["redirect"], use_tls)

def check_http2_support(host: str, port: int=443) -> bool:
    context = ssl.create_default_context()
    context.set_alpn_protocols(["http/1.1", "h2"])
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = context.wrap_socket(s, server_hostname=host)
        s.connect((host, port))
        protocol = s.selected_alpn_protocol()
        s.close()
        return protocol == "h2";
    except ssl.SSLError, OSError:
        return False

def extract_cookies(cookies: list) -> list:
    extracted_cookies = []
    for i in cookies:
        cookie_data = {}
        print(i)
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
    return extracted_cookies

def check_password_protection(status_code):
    return status_code == "401"

def main():
    if len(sys.argv) == 1:
        raise ValueError("Must provide web server.");

    uri_data = parse_uri(sys.argv[1])
    # print(uri_data)

    try:
        use_tls = uri_data["protocol"] == "https"
        try:
            s = open_connection(uri_data["host"], uri_data["port"], use_tls)
        except ssl.SSLError:
            s = open_connection(uri_data["host"], 80)
        
        send_http_request(s, uri_data["filepath"], uri_data["host"])
        header_data = parse_response(receive_response(s))
        if "redirect" in header_data:
            header_data = handle_redirects(header_data["redirect"], use_tls)
        pass_required = check_password_protection(header_data["status"])
        if pass_required or not "host" in header_data:
            http2_support = check_http2_support(uri_data["host"])
        else:
            http2_support = check_http2_support(header_data["host"])
    except socket.gaierror:
        print(f"ERROR: Could not find a website with the hostname {uri_data['host']}")
        sys.exit(1)
    except socket.timeout:
        print(f"ERROR: Did not receive a response from {uri_data['host']}")
        sys.exit(1)
    cookie_list = extract_cookies(header_data["cookies"])
    print(f"Website: {sys.argv[1]}")
    print(f"1. Supports HTTP2: {http2_support}")
    if len(cookie_list) > 0:
        print(f"2. List of Cookies:")
        for c in cookie_list:
            parts = [f"cookie name: {c["name"]}"]
            if "domain" in c:
                parts.append(f"domain name: {c["domain"]}")
            if "expires" in c:
                parts.append(f"expires time: {c["expires"]} ")
            print(", ".join(parts))
    else:
        print("2. No Cookies Provided")
    print(f"3. Password Protected: {pass_required}")
if __name__ == "__main__":
    main()