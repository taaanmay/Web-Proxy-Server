import socket
import _thread
import threading
import sys
#import requests
import datetime
import time
import os
from cmd import Cmd
from urllib.request import Request, urlopen, HTTPError
import select


#Constants
PORT = 8080
SOCKET_IP = socket.gethostbyname(socket.gethostname())      #Get IP Address
ADDR = (SOCKET_IP, PORT)
HTTPS_BUFFER = 8192
HTTP_BUFFER = 4096

MAX_CONNECTIONS = 60
active_connections = 0

cache = {}
blocked = set([])
response_times = {}

#cache_list = {}     # List of Cached Files
#blocked_list = []   # List of Blocked URLs
prev_blocked_list = [] #Previously blokcked URLS



class input_cmd(Cmd):
    prompt = "You >> "

    def do_help(self, args):
        print(" [HOW TO BLOCK] Enter `block` and URL (eg - block www.facebook.com)")
        print(" [HOW TO UNBLOCK] Enter `unblock` and URL (eg - unblock www.facebook.com)")
        print(" [HOW TO SEE BLOCKED URLs] Enter `showblocked` ")
        print(" [HOW TO QUIT PROXY] Enter `quit`")

    def do_block(self, args):
        try:
            arg_URL = args.rsplit(" ", 1)
            arg_URL = arg_URL[0]
        except Exception as error:
            print("Please enter the URL")
        #Adding 'www.' to the URL if not present
        if not "www." in arg_URL:
            arg_URL = "www." + arg_URL
        #Add URL to the blocking list
        blocked.add(arg_URL)
        #Maintaining a Print List of blocked URLs
        if arg_URL not in blocked and len(prev_blocked_list) < 10 :
            prev_blocked_list.append(arg_URL)

        #Printing the blocked URL    
        print("[BLOCKED] : ", arg_URL)


    def do_showblocked(self, args):
        #If there are no URLs blocked, provide suggestions based on the previously blocked URLs that were unblocked
        if blocked == []:
            print("There are no blocked URLs. Some suggestions based on previous activities: ", prev_blocked_list)
        else:    
            print(f"LIST OF BLOCKED URLs : {blocked}")

    def do_unblockall(self, args):
        blocked.clear()
        print("All blocked URLs are unblocked")

    def do_unblock(self, args):
        arg_URL = args.rsplit(" ", 1)
        arg_URL = arg_URL[0]

        #Adding 'www.' to the URL if not present
        if not "www." in arg_URL:
            arg_URL = "www." + arg_URL

        if arg_URL in blocked:
            blocked.remove(arg_URL)
            print("[UNBLOCKED] : ", arg_URL)
        else:
            print("This URL was never blocked")    
    
    def do_quit(self, args):
        print("[QUITTING]: Bye!")
        raise KeyboardInterrupt()




def user_help_method(console, irr):
    console.cmdloop("Enter URL to be blocked: (eg - block www.facebook.com) or help to see available commands.")


def start():
    #Initialise CMD Prompt
    console = input_cmd()
   
    #Multi-Threaded System
    t = threading.Thread(target= user_help_method , args= (console, None))                  #_thread.start_new_thread(user_help_method, (console, None))
    t.start()

    try:    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(ADDR)                                     #Socket is bound to a port
        sock.listen(MAX_CONNECTIONS)
        print(f"[LISTENING] on port {PORT} ")
        log(f"[LISTENING] on port {PORT} ")
    except Exception as error:
        print(f"Error in start method {error}")
        sys.exit(2)   
    
    
    #_thread.start_new_thread(listen_method, (sock,PORT))
    # while(1):
    #     one = 1

    log("[STARTING] Proxy is starting...")
    
    
    global active_connections
    while(active_connections <= MAX_CONNECTIONS):
        try:
            # accept connection from browser
            conn, client_address = sock.accept()

            active_connections = active_connections + 1

            #Data is Received from the browser
            ##data = conn.recv(BUFFER)
            
            # create thread for the connection          
            ##t = threading.Thread(target= requestMethod , args= (conn, data, PORT))            #_thread.start_new_thread(requestMethod, (conn, data, PORT))
            ##t.start()

            #Create New Thread and call proxy_connection method
            thread = threading.Thread(name = client_address, target= proxy_connection , args= (conn, client_address))            #_thread.start_new_thread(requestMethod, (conn, data, PORT))
            thread.setDaemon(True)
            thread.start()
        #except Exception as error:
        except KeyboardInterrupt:
            sock.close()
            ##print(f"[ERROR while listening] : {error}")
            sys.exit(1)

# receive data and parse it, check http vs https
# def proxy_connection(conn, client_address):
# 	global active_connections

# 	# receive data from browser
# 	data = conn.recv(HTTP_BUFFER)
# 	# print(data)
# 	if len(data) > 0:
# 		try:
# 			# get first line of request
# 			request_line = data.decode().split('\n')[0]
# 			try:
# 				method = request_line.split(' ')[0]
# 				url = request_line.split(' ')[1]
# 				if method == 'CONNECT':
# 					type = 'https'
# 				else:
# 					type = 'http'

# 				if check_blocked(url):
# 					active_connections -= 1
# 					conn.close()
# 					return

# 				else:
# 					# need to parse url for webserver and port
# 					print(">> Request: " + request_line)
# 					log(f">> Request:  { request_line}")
                    
# 					webserver = ""
# 					port = -1
# 					tmp = parseURL(url, type)
# 					if len(tmp) > 0:
# 						webserver, port = tmp
# 						# print(webserver)
# 						# print(port)
# 					else:
# 						return      

# 					print(">> Connected to " + webserver + " on port " + str(port))
                    
                    
#                     # log(f">> Connected to   {webserver}  on port  {port}")
                    
                    
					
# 					# check cache for response
# 					start = time.time()
# 					x = cache.get(webserver)
# 					if x is not None:
# 						# if in cache - don't bother setting up socket connection and send the response back
# 						log(">> Sending cached response to user")
#                         #log(">> Sending cached response to user")
						
                        
#                         conn.sendall(x)
						
#                         finish = time.time()
# 						print(f">> [CACHE TIME]: Cache took  + {finish-start):4f} + seconds")
#                         log(f">> [CACHE TIME]: Cache took  + {(finish-start):4f} + seconds")
# 						print(f">> [REQUEST TIME]: Request orignally took + {(response_times[webserver])} + seconds.")
#                         log(f">> [REQUEST TIME]: Request orignally took + {(response_times[webserver])} + seconds.")
					
# 					else:
# 						# connect to web server socket
# 						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 						# sock.connect((webserver, port))

# 						# handle http requests
# 						if type == 'http':
# 							# print("im a http request")
# 							# string builder to build response for cache.
# 							start = time.time()
# 							string_builder = bytearray("", 'utf-8')
# 							sock.connect((webserver, port))

# 							# send client request to server
# 							sock.send(data)
# 							sock.settimeout(2)	

# 							try:
# 								while True:
# 									# try to receive data from the server
# 									webserver_data = sock.recv(HTTP_BUFFER)
# 									# if data is not empty, send it to the browser
# 									if len(webserver_data) > 0:
# 										conn.send(webserver_data)
# 										string_builder.extend(webserver_data)
# 									# communication is stopped when a zero length of chunk is received
# 									else:
# 										break
# 							except socket.error:
# 								pass
						
# 							# communication is over so can now store the response_time and response which was built
# 							finish = time.time()
# 							print(f">> [CACHE MISS]: Request took + {(response_times[webserver])} + seconds.")
#                             log(f">> [CACHE MISS]: Request orignally took + {(response_times[webserver])} + seconds.")
# 							response_times[webserver] = finish - start 
# 							cache[webserver] = string_builder
# 							print(">> Added to cache: " + webserver)
#                             log(">> Added to cache: " + webserver)
# 							active_connections -= 1
# 							sock.close()
# 							conn.close()

# 						# handle https requests
# 						elif type == 'https':
# 							sock.connect((webserver, port))
# 							# print("im a https request")
# 							conn.send(bytes("HTTP/1.1 200 Connection Established\r\n\r\n", "utf8"))
							
# 							connections = [conn, sock]
# 							keep_connection = True

# 							while keep_connection:
# 								ready_sockets, sockets_for_writing, error_sockets = select.select(connections, [], connections, 100)
								
# 								if error_sockets:
# 									break
								
# 								for ready_sock in ready_sockets:
# 									# look for ready sock
# 									other = connections[1] if ready_sock is connections[0] else connections[0]

# 								try:
# 									data = ready_sock.recv(HTTPS_BUFFER)
# 								except socket.error:
# 									print(">> Connection timeout...")
# 									ready_sock.close()

# 								if data:
# 									other.sendall(data)
# 									keep_connection = True
# 								else:
# 									keep_connection = False
			
#             except IndexError:
# 				pass
# 		except UnicodeDecodeError:
# 			pass
# 	else:
# 		pass				

# receive data and parse it, check http vs https
def proxy_connection(conn, client_address):
	global active_connections

	# receive data from browser
	data = conn.recv(HTTP_BUFFER)
	# print(data)
	if len(data) > 0:
		try:
			# get first line of request
			request_line = data.decode().split('\n')[0]
			try:
				method = request_line.split(' ')[0]
				url = request_line.split(' ')[1]
				if method == 'CONNECT':
					type = 'https'
				else:
					type = 'http'

				if check_blocked(url):
					active_connections -= 1
					conn.close()
					return

				else:
					# need to parse url for webserver and port
					print(">> Request: " + request_line)
					log(">> Request: " + request_line)
					webserver = ""
					port = -1
					tmp = parseURL(url, type)
					if len(tmp) > 0:
						webserver, port = tmp
						# print(webserver)
						# print(port)
					else:
						return 

					print(">> Connected to " + webserver + " on port " + str(port))
					log(">> Connected to " + webserver + " on port " + str(port))
					
					# check cache for response
					start = time.time()
					x = cache.get(webserver)
					if x is not None:
						# if in cache - don't bother setting up socket connection and send the response back
						print(">> Sending cached response to user")
						log(">> Sending cached response to user")
						conn.sendall(x)
						finish = time.time()
						time_taken = finish-start
						print(f"Request took: {finish - start:0.4f} seconds")
						log(f"Request took: {finish - start:0.4f} seconds")
						#print(f">> Request took: " + {finish-start:0.4f} + "s with cache.")
						print(">> Request took: " + str(response_times[webserver]) + "s without cache.")
						log(">> Request took: " + str(response_times[webserver]) + "s without cache.")
					
					else:
						# connect to web server socket
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						# sock.connect((webserver, port))

						# handle http requests
						if type == 'http':
							# print("im a http request")
							# string builder to build response for cache.
							start = time.time()
							string_builder = bytearray("", 'utf-8')
							sock.connect((webserver, port))

							# send client request to server
							sock.send(data)
							sock.settimeout(2)	

							try:
								while True:
									# try to receive data from the server
									webserver_data = sock.recv(HTTP_BUFFER)
									# if data is not empty, send it to the browser
									if len(webserver_data) > 0:
										conn.send(webserver_data)
										string_builder.extend(webserver_data)
									# communication is stopped when a zero length of chunk is received
									else:
										break
							except socket.error:
								pass
						
							# communication is over so can now store the response_time and response which was built
							finish = time.time()
							print(">> Request took: " + str(finish-start) + "s")
							log(">> Request took: " + str(finish-start) + "s")
							response_times[webserver] = finish - start 
							cache[webserver] = string_builder
							print(">> Added to cache: " + webserver)
							log(">> Added to cache: " + webserver)
							active_connections -= 1
							sock.close()
							conn.close()

						# handle https requests
						elif type == 'https':
							sock.connect((webserver, port))
							# print("im a https request")
							conn.send(bytes("HTTP/1.1 200 Connection Established\r\n\r\n", "utf8"))
							
							connections = [conn, sock]
							keep_connection = True

							while keep_connection:
								ready_sockets, sockets_for_writing, error_sockets = select.select(connections, [], connections, 100)
								
								if error_sockets:
									break
								
								for ready_sock in ready_sockets:
									# look for ready sock
									other = connections[1] if ready_sock is connections[0] else connections[0]

								try:
									data = ready_sock.recv(HTTPS_BUFFER)
								except socket.error:
									print(">> Connection timeout...")
									ready_sock.close()

								if data:
									other.sendall(data)
									keep_connection = True
								else:
									keep_connection = False
			except IndexError:
				pass
		except UnicodeDecodeError:
			pass
	else:
		pass				
	
	# active_connections -= 1
	# print(">> Closing client connection...")
	# conn.close()
	# return


def parseURL(url, type):
    http_position = url.find("://")

    # Type of request
    if (http_position == -1):
        temp = url
    else:    
        temp = url[(http_position+3):]
        
    # Obtaining Port position and Base from the Request
    port_position = temp.find(":")
    webserver_position = temp.find("/")

    if webserver_position == -1:
        webserver_position = len(temp)

    webserver = ""
    port = -1

    #DEFAULT PORT
    if port_position == -1 or webserver_position < port_position:
        if type == "https":
            port = 443
        else:
            port = 80
        
        webserver = temp[:webserver_position]
	# defined port
    else:												
	    port = int((temp[(port_position+1):])[:webserver_position-port_position-1])
	    webserver = temp[:port_position]

    return [webserver, int(port)]




def check_blocked(url):
    for temp_url in blocked:
        if temp_url in url:
            print(f"[BLOCKED]: {url} is blocked")
            log(f"[BLOCKED]: {url} is blocked")
            return True
    return False



# Logs all the information that would be too much to send to the commandline.
def log(input):
    
    currTime = datetime.datetime.now().strftime("%Y-%m-%d")
    newFile = "/Users/tanmaykaushik/Desktop/modify/logs" + str(currTime) + ".txt"
    newFile = newFile.replace(' ', '_')
    newFile = newFile.replace(':', '_')
    newFile = "" + newFile
    file = open(newFile, "a")
    file.write("\n" + input)
    file.flush()






print("[STARTING] Proxy is starting...")
start()
