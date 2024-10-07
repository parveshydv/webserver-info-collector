#!/usr/bin/python3


import socket
import sys
import re
import ssl

DEFAULT_HTTP_PORT = 80
DEFAULT_HTTPS_PORT = 443
HTTP_SUPPORTING_CODES = [2, 3]


def main():

    cookieList = []
    cookieJar = []
    http2Support = False
    passwordProtected = False

    inputVar = getUserInput()
    inputParsed = parseUserInput(inputVar)

    #HTTPS
    dataHTTPS = httpsTest(inputParsed)
    if dataHTTPS != "":
        httpsSupport, cookieJar, passwordProtected = processResponse(dataHTTPS)
        # cookies
        if cookieJar:
            cookieList.extend(cookieJar)
        
        #check for Http2
        http2Support = http2Test(inputParsed)

    if cookieJar:
        cookieList.extend(cookieJar)
    
    print("website: "+ inputParsed[1])

    print("1. Supports http2: " + ("yes" if http2Support  else "no"))
    
    print("2. List of Cookies:")
    for cookie in cookieList:
        print(*cookie, sep = ", ")

    print("3. Password-protected: " + ("yes" if passwordProtected else "no"))




def http2Test(formattedInput):
    # Prepare SSL context with appropriate protocol and cipher settings
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20")
    ssl_context.set_alpn_protocols(['h2', 'HTTP/1.1'])
    ssl_context.options |= ssl.OP_NO_COMPRESSION

    # Initialize socket connection
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print(f"Socket initialization failed: {err}")
        return None

    # Attempt to connect to the server on the default HTTPS port
    try:
        sock.connect((formattedInput[1], DEFAULT_HTTPS_PORT))
    except socket.error as err:
        print(f"Connection attempt failed: {err}")
        return None

    try:
        secure_sock = ssl_context.wrap_socket(sock, server_hostname=formattedInput[1])
    except ssl.SSLError as err:
        print(f"SSL wrapping failed: {err}")
        return None

    try:
        protocol = secure_sock.selected_alpn_protocol()
    except ssl.SSLError as err:
        print(f"Protocol negotiation failed: {err}")
        return None

    # Return True if HTTP/2 is supported, otherwise return an empty string
    return True if protocol else ""




def httpsTest(formattedInput):
    # Set up SSL context with HTTP/1.1 protocol and necessary ciphers
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_alpn_protocols(["HTTP/1.1"])
    ssl_context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20")
    ssl_context.options |= ssl.OP_NO_COMPRESSION

    # Prepare HTTP request
    request = f"GET / HTTP/1.1\r\nHOST: {formattedInput[1]}\r\nCONNECTION: Keep-Alive\r\n\r\n"
    request_encoded = request.encode("UTF-8", errors="ignore")

    # Create and wrap socket with SSL
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl_context.wrap_socket(sock, server_hostname=formattedInput[1])
    except socket.error as e:
        print(f"Socket error: {e}")
        return ""

    # Send the HTTPS request and handle response
    try:
        ssl_sock.connect((formattedInput[1], DEFAULT_HTTPS_PORT))
        ssl_sock.sendall(request_encoded)
        response = ssl_sock.recv(10000).decode(errors="ignore")
        ssl_sock.close()
        return response
    except (socket.timeout, socket.gaierror) as e:
        print(f"Connection error: {e}")
        return ""

def processResponse(data):
    cookieList = []

    startBody = data.find("\r\n\r\n")
    headData = data[:startBody]
    bodyData = data[startBody+4:]
    
    #print("---Response header ---")
    #print(headData+"\n")
    #print("---Response body ---")
    #print(bodyData+"\n")

    headDataList = convert(headData)
    firstLine = headDataList[0]
    code = firstLine.split()
    codeType = int(code[1][0])
    isSupported = codeType in HTTP_SUPPORTING_CODES

    # Determine if password protection is required
    password_protected = codeType == 401

    # cookie 
    for line in headDataList:
        if line.startswith("Set-Cookie:"):
            cookie = []
            cookieStart = line[12:]
            cookieStart = cookieStart.split("; ")
            for item in cookieStart:
                if "=" in item:
                    cookieElement = item.split("=")
                    if cookie == []:
                        cookieElement[0] = "cookie name: "+cookieElement[0]
                        cookie.append(cookieElement[0])

                    if "expires" in cookieElement[0]:
                        cookieElement[0]= cookieElement[0] +":"
                        cookie.append(' '.join(cookieElement))
                    elif "Expires" in cookieElement[0]:
                        cookieElement[0]= cookieElement[0] +":"
                        cookieElement=' '.join(cookieElement)
                        cookie.append(cookieElement)

                    if "domain" in cookieElement[0]:
                        cookieElement[0]= cookieElement[0] +":"
                        cookie.append(' '.join(cookieElement))
                    elif "Domain" in cookieElement[0]:
                        cookieElement[0]= cookieElement[0] +":"
                        cookieElement=' '.join(cookieElement)
                        cookie.append(cookieElement)
            cookieList.append(cookie)
    return isSupported, cookieList, password_protected



def getUserInput():
    uriPattern = r"^([\w\-\.\+]+(\:\/\/))?([\w\-\.])+((\:)[0-9]+)?([\w\-\/\?\#\&\;\.]*)?$"

    if len(sys.argv) == 2:
        if re.match(uriPattern, sys.argv[1]):
            return sys.argv[1]
        print("Invalid URI format, please verify.\n")
        return sys.argv[1]

    if len(sys.argv) == 1:
        userInput = input("No URI argument found, please enter one:")
        if not userInput:
            print("Empty input, exiting.")
            sys.exit()
        return userInput

    print("Too many arguments.")
    sys.exit()


def parseUserInput(uri):
    # Split URI based on "://", protocol extraction
    parts = uri.split("://", 1)
    protocol = parts[0] if len(parts) > 1 else None
    uriItter = parts[1] if len(parts) > 1 else parts[0]

    # Split by first '/', host and path extraction
    host_path_split = uriItter.split("/", 1)
    host_part = host_path_split[0]
    path = host_path_split[1] if len(host_path_split) > 1 else None

    host_port_split = host_part.split(":", 1)
    host = host_port_split[0]
    port = host_port_split[1] if len(host_port_split) > 1 else None

    return [protocol, host, port, path]




def convert(string): 
    li = string.splitlines()
    return li

if __name__ == '__main__':
    main()
