WebTester is a Python-based tool designed to collect and display information about a web server. This project provides experience with socket programming in Python and focuses on HTTP application-layer protocols.

WebTester connects to a web server and provides details on:

1. Whether the web server supports HTTP/2.
2. Cookies (name, expiry time, and domain) set by the server.
3. Whether the web page is password-protected.


Project Background

1. HTTP: The Hypertext Transfer Protocol facilitates communication among web servers. WebTester sends HTTP requests and parses responses to extract key inform
ation.HTTP: The Hypertext Transfer Protocol facilitates communication among web servers. WebTester sends HTTP requests and parses responses to extract key information.

2. URI: Uniform Resource Identifiers identify network resources and have the format protocol://host[:port]/filepath.


Installation and Usage

1. Clone the repository:
   git clone https://github.com/yourusername/WebTester.git


2. Navigate to the project directory:
    cd WebTester

3. Run the WebTester tool with a website URI as an argument:
   python3 WebTester.py <website-URI>
