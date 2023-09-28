#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        # print ("Got a request of: %s\n" % self.data)
        request_line = self.data.splitlines()[0]
        method, path, _ = request_line.split()
        
        root_dir = "www"
        filepath = os.path.join(root_dir, path.lstrip("/"))
        if method != 'GET':
            self.send_response(405,"Method Not Allowed")
            return
        if ".." in path:
            self.send_response(404, "Not Found")
            return
        if os.path.isdir(filepath) and not path.endswith("/"):
            self.send_redirect_response(path + "/")
            return
        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, "index.html")
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                content = file.read()
                mime_type, _ = mimetypes.guess_type(filepath)
                self.send_response(200, "OK", content, mime_type)
        else:
            self.send_response(404, "Not Found")



    def send_response(self, status_code, status_msg, content="", mime_type="text/html"):
        response = f"HTTP/1.1 {status_code} {status_msg}\r\n"
        response += f"Content-Type: {mime_type}\r\n"
        response += f"Content-Length: {len(content)}\r\n\r\n"
        response += content
        self.request.sendall(bytearray(response, 'utf-8'))

    def send_redirect_response(self, location):
        response = f"HTTP/1.1 301 Moved Permanently\r\n"
        response += f"Location: {location}\r\n\r\n"
        self.request.sendall(bytearray(response, 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
