# Must be able to do the following:
# Confirm whether or not the web server support https
# Cookie name, expiry time (if any), domain name (in any) of cookies that the web server will use
# Whether or not the requested web page is password-protected

# First accept URI from stdin and process it.
# Connect to the server
# Send an HTTP request, and recieve an HTTP response
# Print the response from the server, marking the header and body.
import socket
import sys

def parse_uri(uri: str) -> tuple:
    uri_data = {}
    uri = uri.split("://", 1)
    uri_data["protocol"] = uri[0]
    print(uri)
    uri = uri[1].split(":", 1)
    uri_data["host"] = uri[0]
    print(uri)
    uri = uri[1].split("/", 1)
    uri_data["port"] = uri[0]
    uri_data["fp"] = "/" + uri[1]
    print(uri)
    print(uri_data)
def open_connection(host, port,use_tls):
    pass
def send_http_request(sock, request):
    pass;
def recieve_response(sock):
    pass;
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
    uri_data = parse_uri(sys.argv[1]);
    
if __name__ == "__main__":
    main()