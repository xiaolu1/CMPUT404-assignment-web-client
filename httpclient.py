#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def parseURL(self, url):
        step1 = re.search('(https?)://(?P<netloc>[^/?#]+)(?P<path>.*)', url)
        step2 = step1.group('netloc').split(':')
        if len(step2) == 1:
            port = 80
        else:
            port = int(step2[1])
        
        host = step2[0]
        if (step1.group('path')):
            path = step1.group('path')
        else:
            path = "/"
            
        return port, host, path
    
    def connect(self, host, port):
        # use sockets!
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s

    def get_code(self, data):
        code = int(data.split()[1])
        return code

    def get_headers(self, method, path, host, data):
        header = method + " " + path + " HTTP/1.1 \r\nHost: " + host + "\r\n"
        header += "Accept: text/html,text/plain,text/css \r\n"
        header += "Connection: close "
        if (method =="POST"):
            header += "Content-Type: application/x-www-form-urlencoded\r\n"
            header += "Content-Length: " + str(len(data))
        header += "\r\n\r\n"
        header += data
        return header

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def send(self, method, url, data = ""):
        port, host, path = self.parseURL(url)
        
        socket = self.connect(host, port)
        request = self.get_headers(method, path, host, data)
        socket.sendall(request)
        response = self.recvall(socket)

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def GET(self, url, args=None):
        return self.send("GET", url)

    def POST(self, url, args=None):
        data = ""
        if (args != None):
            data = urllib.urlencode(args)
        return self.send("POST", url, data)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )