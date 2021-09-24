#  coding: utf-8 
import socketserver
from urllib.parse import urlparse
import os
from os import path

'''
Copyright 2021 Aaron Tripodi

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and 
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

'''



class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        

        # First, take the request info, parse it, 
        request_info = urlparse(self.data)
        
        # and split it up in to pieces we can use
        split_request = request_info.path.split()
     
        
        print(split_request)

        # below we are doing all of the checks for the requests in the assignment instructions. 
        # The main 2 chekcs are index and css
        if '/index.html'.encode() in split_request[1]:
            if split_request[1].endswith('/'.encode()):
               default_response(self)
            else:
                print("index.html request")
                f = getFile(path.relpath('www/index.html'))
                encode_and_send(f, 'text/html', self)
        elif '/base.css'.encode() in split_request[1]:
            if split_request[1].endswith('/'.encode()):
               default_response(self)
            else:
                print("base.css request")
                f = getFile(path.relpath('www/base.css'))
                encode_and_send(f, 'text/css', self)
        # check for deep
        elif '/deep'.encode() in split_request[1]:  #and '/base.css'.encode() or '/index.html'.encode() in split_request[1]:
            default_response(self)
        elif split_request[1] == '/'.encode():
            default_response(self)
        # this specific check looks for a PUT request, and should return a 405 error
        elif split_request[0] == 'PUT'.encode():
           self.request.sendall(str.encode("HTTP/1.0 405 METHOD NOT ALLOWED\r\n",))
           self.request.sendall(str.encode("Pragma: no-cache\r\n"))
           self.request.sendall(str.encode("Location: http://127.0.0.1:8080/\r\n"))
           self.request.sendall(str.encode('Content-Type: application/octet-stream\r\n'))
           self.request.send(str.encode('\r\n'))
        # everything else returns 404
        else:
           self.request.sendall(str.encode("HTTP/1.0 404 NOT FOUND\r\n",))
           self.request.sendall(str.encode("Pragma: no-cache\r\n"))
           self.request.sendall(str.encode("Location: http://127.0.0.1:8080/\r\n"))
           self.request.sendall(str.encode('Content-Type: application/octet-stream\r\n'))
           self.request.send(str.encode('\r\n'))


# this is a function I wrote to handle a lot of the situaions, it just defaults to the html page
def default_response(self):
    print("index.html request")
    f = getFile(path.relpath('www/index.html'))
    encode_and_send(f, 'text/html', self)


# This function handles all 200 OK responses and sends the data to the page
def encode_and_send(f, content_type, self):
    assert type(content_type) == str
    # code below is used from https://stackoverflow.com/questions/47726865/html-page-not-displaying-using-python-socket-programming
    #===================
    self.request.sendall(str.encode("HTTP/1.0 200 OK\r\n",))
    self.request.sendall(str.encode("Pragma: no-cache\r\n"))
    self.request.sendall(str.encode("Location: http://127.0.0.1:8080/\r\n"))
    self.request.sendall(str.encode('Content-Type: '+content_type+'\r\n'))
    self.request.send(str.encode('\r\n'))
    # send data per line
    for l in f.readlines():
        print('Sent ', repr(l))
        self.request.sendall(str.encode(""+l+""))
        l = f.read(1024)
    f.close()
    # =================
    

# a simple file opening function
def getFile(name):
        if os.path.isfile(name):
           f = open(name, 'r',)
           print(name + " opened")
           return f
        else:
            print("file doesn't exist")
        
        


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
