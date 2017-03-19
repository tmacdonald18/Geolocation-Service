#   Author: Tyler MacDonald <tcmacd18@g.holycross.edu>
#   Date:   14 March 2017
#   Program:    central.py
#   Purpose:    Runs the central coordinator server in the geolocation program

import os
import socket
import sys
import urllib
import time
import threading

# Returns the form
def handle_form_request(i):
    print i, ": Handling form request"
    data = open(form).read()
    return("200 OK", "text/html", data)

def handle_geolocate_request(name, i):
    #TODO

def handle_pinger_connection(

def handle_hello_request(i):
    print i, ": Handling hello request"
    return ("200 OK",
            "text/plain",
            "Why, hello yourself!\n")

def handle_hello_name_request(name, i):
    print i, ": Handling hello-name request"
    return ("200 OK",
            "text/plain",
            "Why, hello %s! How are you doing today?\n" % (name))

# handle_file_request returns a status code, mime-type, and the body of a file
def handle_file_request(path, i):
    global num_errors
    print i, ": Handling file request for", str(path)
    try:
        if not os.path.isfile(path):
            print i, ": File was not found: " + str(path)
            num_errors = num_errors + 1
            return ("404 NOT FOUND", "text/plain", "No such file: " + path)
        data = open(path).read()
    except:
        print i, ": Error encountered reading from file"
        num_errors = num_errors + 1
        return ("403 FORBIDDEN", "text/plain", "Permission denied: " + path)
    mime_type = get_mime_type(path)
    return ("200 OK", mime_type, data)

# handle_request() returns a status code, mime-type, and body for the given url
def handle_request(url, i):
    global num_errors
    url = urllib.unquote(url)
    if url == "/status":
        return handle_status_request(i)
    elif url == "/hello":
        return handle_hello_request(i)

    elif url == "midnight":
        return handle_pinger_connection(i)
    elif url == "/" or "/index.html":
        return handle_form_request(i)
    elif url.startswith("/geolocate"):
        name = url[18:]
        return handle_geolocate_request(name, i)
    
    elif url.startswith("/hello?"):
        name = url[7:]
        return handle_hello_name_request(name, i)
    elif url.startswith("/"):
        path = '/' + url[1:]
        return handle_file_request(path, i)
    else:
        print i, ": Unrecognized url prefix"
        num_errors = num_errors + 1
        return ("404 NOT FOUND", "text/plain", "No such resource: " + url)


# get_mime_type() tries to get the file extension
def get_mime_type(path):
    path = path.lower()
    if path.endswith('.jpg') or path.endswith('.jpeg'):
        return 'image/jpeg'
    elif path.endswith('.png'):
        return 'image/png'
    elif path.endswith('.txt'):
        return 'text/plain'
    elif path.endswith('.css'):
        return 'text/css'
    elif path.endswith('.js'):
        return 'application/javascript'
    else:
        return 'text/html'

# Reads an HTTP request from socket c, parses and handles the request, then sends the response back to socket c
def handle_http_connection(c, client_addr, i):
   
    global num_errors, num_requests, tot_time, avg_time, max_time
    print i, ": Handling connection from", client_addr
    keep_alive = True
    data = ""
    j = 0
    while keep_alive:
        num_requests = num_requests + 1
        j = j + 1
        start = time.time()
        keep_alive, data = handle_one_http_request (c, data, i)
        
        # Do end-of-request statistics and cleanup
        end = time.time()
        print i, ": Handled request", j, "from", client_addr
        
        # Update status/performance counters
        duration = end - start
        tot_time = tot_time + (end - start)
        avg_time = tot_time / num_requests
        if duration > max_time:
            max_time = duration
    c.close()
    print i, ": Done with connection from", client_addr

# Reads one HTTP request
def handle_one_http_request(c, data, i):
    
    #keep reading from socket until we reach a "\r\n\r\n"
    while "\r\n\r\n" not in data:
        try:
            more_data = c.recv(4096)
            if not more_data:
                return (False, data)
            data = data + more_data
        except:
            print i, ": Error reading from socket"
            return (False, data)
    if (data == "midnight"):
        keep_alive = True
        socket_list.append(c)
        
    else:
        request, data = data.split("\r\n\r\n", 1)
        first_line, headers = request.split("\r\n", 1)
        print i, ": Request is:", first_line
        method, url, version = first_line.split()
        print i, ": Method is", method, "url is", url, "version is", version
    
        # If version is HTTP/1.1 and "Connection: keep-alive" is in the headers
        keep_alive = (version == "HTTP/1.1" and "Connection: keep_alive" in headers)
        code, mime_type, body = handle_request(url, i)
        c.sendall("HTTP/1.1 " + code + "\r\n")
        c.sendall("Server: Dream Team\r\n")
        c.sendall("Date: " + time.strftime("%a, %d %b %Y %H:%M:%S %Z") + "\r\n")
        c.sendall("Content-Type: " + mime_type + "\r\n")
        c.sendall("Content-Length: " + str(len(body)) + "\r\n")
        if keep_alive:
            c.sendall("Connection: keep-alive\r\n")
        else:
            c.sendall("Connection: close\r\n")
        c.sendall("\r\n")
        c.sendall(body)
        
    return (keep_alive, data)


# Main function to be called in geolocate.py
def run_central_coordinator(my_ipaddr, my_zone, my_region, central_host, central_port):

    #initialize socket_list
    socket_list = []

    # Print a welcome message
    server_addr = (central_host, central_port)
    print "Starting web server"
    print "Listening on address", server_addr
    print "Serving files from", server_root

    # Create server socket and set it up
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(server_addr)
    s.listen(5)

    try:
        # Repeatedly accept and handle connections
        while True:
            c, client_addr = s.accept()
            num_connections = num_connections + 1
            i = num_connections
            t = threading.Thread(target=handle_http_connection, args=(c, client_addr, i))
            t.daemon = True
            t.start()
    finally:
        print 'Server is shutting down'
        s.close()
