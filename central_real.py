#   Author: Tyler MacDonald and Lucca Eloy f<tcmacd18@g.holycross.edu>
#   Date:   21 March 2017
#   Program:    central.py
#   Purpose:    Runs the central coordinator server in the geolocation program

import os
import socket
import sys
import urllib
import time
import threading

server_host = ""
server_port = 8888
server_root = "./web_files"

# Returns a created socket
def createSocket():
    print 'Creating socket.'
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
# Returns a URL parsed into a list of host, port and path
def parseURL(url):
	# check for formatting
	if "http://" in url:
		return parseURL(url[7:])
	elif "https://" in url:
		return parseURL(url[8:])
	# parsing
	elif "/" in url:
		parsedURL = url.split("/", 1)
		if ":" in parsedURL[0]:
			temp = parsedURL[0].split(":", 1)
			temp.append(parsedURL[1])
			return temp
		else:
			return parsedURL

# Fetching Target URL
def fetchTargetURL(url):

	#splits URL into host, port and path
	splitURL = parseURL(url)
	
	if len(splitURL) == 2:
		host = splitURL[0]
		path = splitURL[1]
		port = 80
	elif len(splitURL) == 3:
		host = splitURL[0]
		port = int(splitURL[1])
		path = splitURL[2]
		
	serverAddress = (host, port)
	
	#opens socket and connects to host:port
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(serverAddress)
	
	#creates valid HTTP GET request with given path, including minimal headers
	request_line = "GET /" + path + " HTTP/1.1"
	host_name_header = "Host: " + host
	end = "\r\n\r\n"
	
	httpRequest = request_line + "\r\n" + host_name_header + end
	print httpRequest
	
	#sends request to url
	print "Sending Request."
	sock.sendall(httpRequest)
	
	#receives html response--at least 1 byte of it
	print "Receiving html response."
	htmlResponse = sock.recv(4096)
	
	#returns an HTML response
	print "Returning html response."
	return htmlResponse

# Sends HTML response containing homepage
def handle_index_request(c):
	print "Handling index request"
	data = open("index.html").read()
	currentDate = time.strftime('%c %Z')
	serverName = 'Midnight'
	lastModified = 'Sun, 03/19/17 15:37:00 Eastern Standard Time'
	contentLength = str(len(data))
	connectionType = 'close'
	contentType = 'text/html'
	
	#concatonate and format
	r = 'HTTP/1.1 200 OK\r\nDate: ' + currentDate + '\r\nServer: ' + serverName + '\r\nLast-Modified: ' + lastModified + '\r\nContent-Length: ' + contentLength + '\r\nConnection: ' + connectionType + '\r\nContent-Type: ' + contentType + '\r\n\r\n' + data
	
	#sendall
	c.sendall(r)
	print 'Sent response, content length was ' + contentLength

# Sends HTML response containing error page	
def handle_error_response(c):
	print "Handling error reponse"
	data = "<h1>404 NOT FOUND. USE PATH /index.html FOR HOMEPAGE.</h1>"
	currentDate = time.strftime('%c %Z')
	serverName = 'Midnight'
	lastModified = 'Sun, 03/19/17 15:37:00 Eastern Standard Time'
	contentLength = str(len(data))
	connectionType = 'close'
	contentType = 'text/html'
	
	#concatonate and format
	r = 'HTTP/1.1 200 OK\r\nDate: ' + currentDate + '\r\nServer: ' + serverName + '\r\nLast-Modified: ' + lastModified + '\r\nContent-Length: ' + contentLength + '\r\nConnection: ' + connectionType + '\r\nContent-Type: ' + contentType + '\r\n\r\n' + data
	
	#sendall
	c.sendall(r)
	print 'Sent response, content length was ' + contentLength

# Reads an HTTP request from socket c, parses and handles the request, then sends the response back to socket c
def handle_http_connection(c, client_addr):
   
    global num_errors, num_requests, tot_time, avg_time, max_time
    print "Handling connection from", client_addr
    keep_alive = True
    data = ""
    while keep_alive:
        keep_alive, data = handle_one_http_request (c, data)
    c.close()
    print "Done with connection from", client_addr

# Reads one HTTP request
def handle_one_http_request(c, data):
    
	data = c.recv(4096)
	
	if (data == "midnight"):
		keep_alive = True
		socket_list.append(c)
		print socket_list
	else:
		#attempt to split message
		try:
			s = message.splitlines()
			s = s[0].split()
		except:
			handle_error_response()
		
		if s[0] == 'GET':
			path = s[1]
			print 'Request path: ' + path
			
			if '/index.html' == path or '/' == path or '/index' == path:
				keep_alive = False
				handle_index_request(c)
			else:
				keep_alive = False
				handle_error_response(c)

	return (keep_alive, data)


# Main function to be called in geolocate.py
def run_central_coordinator(my_ipaddr, my_zone, my_region, central_host, central_port):

    #initialize socket_list
    socket_list = []

    if len(sys.argv) >= 2:
	server_port = int(sys.argv[2])
    if len(sys.argv) >= 3:
	server_root = sys.argv[1]
	
    # Print a welcome message
    server_addr = (server_host, server_port)
    central_addr = (central_host, central_port)
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
            t = threading.Thread(target=handle_http_connection, args=(c, client_addr))
            t.daemon = True
            t.start()
    finally:
        print 'Server is shutting down'
        s.close()
