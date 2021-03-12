import socket
import _thread
import sys
#import requests
import time
import os
from urllib.request import Request, urlopen, HTTPError



#Constants
PORT = 8080
SOCKET_IP = socket.gethostbyname(socket.gethostname())      #Get IP Address
ADDR = (SOCKET_IP, PORT)
BUFFER = 8192
MAX_CONNECTIONS = 5

cache_list = []  # List of Cached Websites



def start():

    try:    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(ADDR)                                     #Socket is bound to a port
        sock.listen(MAX_CONNECTIONS)
    except Exception as error:
        print(f"Error in start method {error}")
        sys.exit(2)   

    print(f"[LISTENING] on port {PORT} ")
    _thread.start_new_thread(listen_method, (sock,PORT))

    while(1):
        one = 1


# def start():
#     try:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.bind(('127.0.0.1', 8080))
#         sock.listen(MAX_CONNECTIONS)
#         print("Server started successfully!")
#     except Exception as e:
#         print(e)
#         sys.exit(2)
    
#     print("Starting to listen for connections...")
#     _thread.start_new_thread(listen_method, (sock, 8080)) #Call to listen

#     while(1):
#         one = 1

     
#LISTENER METHOD - Listens for Request on the port selected by the user. Current Port - 8080
def listen_method(sock, port):
    
    while(1):
        try:
            # accept connection from browser
            conn, _ = sock.accept()
            
            #Data is Received from the browser
            data = conn.recv(BUFFER)
            
            # create thread for the connection          
            _thread.start_new_thread(requestMethod, (conn, data, port))
        except Exception as error:
            sock.close()
            print(f"[ERROR while listening] : {error}")
            sys.exit(1)


def requestMethod(conn, data, port):
    try:
        encoding = 'utf-8'

       #Data is decoded as the data received is in Bytes
        data = data.decode(encoding)
        
        #First Line of request
        request_line = data.split('\n')[0]
        request_line = request_line.split(' ')

        #Check Method Type from the request to see if HTTP or HTTPS Request
        method_type = request_line[0]

        #Obtaining URL
        url = request_line[1]
        http_position = url.find("://")


        if (http_position == -1):
            temp = url
        
        elif method_type == "GET":      #HTTP Request
            temp = url[(http_position+3):]
        
        else:                           #HTTPS Request
            temp = url[(http_position+4):]
        
        port_position = temp.find(":")

        base_URL_position = temp.find("/")

        if base_URL_position == -1:
            base_URL_position = len(temp)
        
        baseURL = ""

        port = -1


        # Default port.
        if port_position == -1 or base_URL_position < port_position:
            port = 8080
            baseURL = temp[:base_URL_position]
        
        # Specific port.
        else:
            port = int((temp[(port_position+1):])[:base_URL_position-port_position-1])
            baseURL = temp[:port_position]
        
        # Re-encode the data into bytes.
        data = data.encode(encoding)
        proxy_method(baseURL, port, conn, data, method_type, url)
    except Exception as e:
        pass

def proxy_method(baseURL, port, conn, data, method_type, url):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if method_type == "CONNECT":
        try:
           
            sock.connect((baseURL, port))
            reply = "HTTP/1.0 200 Connection established\r\nProxy-agent: Tanmay_Proxy\r\n\r\n"
            conn.sendall(reply.encode())
        
        except socket.error as e:
            print(f"[ERROR in proxy mehthod {e}")
            return

        conn.setblocking(0)
        sock.setblocking(0)

        while True:
            try:
                request = conn.recv(BUFFER)
                sock.sendall(request)
            except socket.error as e:
                pass
            
            
            try:
                reply = sock.recv(BUFFER)
                conn.sendall(reply)
                dar = float(len(reply))
                dar = float(dar/1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                #print("Request Complete: %s -> %s <- " % (str(baseURL), str(dar)))
            except socket.error as e:
                pass
   
   
    else:
   
        if baseURL not in cache_list:
            time_counter_start = time.perf_counter()
            sock.connect((baseURL, port))
            sock.send(data)
            
            #Add Website to Cache List
            cache_list.append(baseURL)
            print("This request has never been cached. ")
            
            #Fetch file from server
            file_server = request_server(url)

            if file_server:
                store_cache(url, baseURL, file_server)

            time_counter_stop = time.perf_counter()
            #Time Taken to fetch file from server
            print(f"\n[REQUEST TIME TAKEN] - {time_counter_stop - time_counter_start} seconds")


            try:
                while True:
                    reply = sock.recv(BUFFER)
                    if (len(reply) > 0):
                        conn.send(reply)
                        dar = float(len(reply))
                        dar = float(dar/1024)
                        dar = "%.3s" % (str(dar))
                        dar = "%s KB" % (dar)
                        #print("Request Complete: %s -> %s <- " % (str(baseURL), str(dar)))
                    else:
                        break
                sock.close()
                conn.close

            except socket.error:
                sock.close()
                conn.close()
                sys.exit(1)
        
        else:

            # #print(f"[CONTENT]: {content}")
            # #print(content)
            clock_start = time.perf_counter()
            content = request_cache(baseURL)
            #print(f"[CONTENT]: {content}")
            clock_stop = time.perf_counter()

            #Time taken to fetch file by cache 
            print(f"[CACHE TIME TAKEN] - {clock_stop - clock_start} seconds")
            
            response = 'HTTP/1.0 200 OK\n\n' + content
            conn.send(response.encode())


    sock.close()
    conn.close()

       

# #Method where uncached request is requested from the server
def request_server(url):
    data = Request(url)
    try:
        resp = urlopen(data)
        # Header decoded from the request
        resp_header = resp.info()

        # Content decoded from the request
        content = resp.read().decode('utf-8')

        return content
    except HTTPError:
        return None

# #Method to retreive request which has been stored in the cache previously
def request_cache(baseURL):
    try:
        file_input = open(baseURL)    # Open baseURL from local file
        content = file_input.read()
        file_input.close()
        return content          # Return retreived file
    except IOError:
        return None   


def store_cache(url, baseURL, file_server):
    print('Saving a copy of {} in the cache'.format(url))
    try:
        cache_file = open(baseURL, 'w') #Open Cache File using base
    except Exception as e:
        print(f"[ERROR] Opening Cache File: {e}")    
    cache_file.write(file_server)
    cache_file.close()    







print("[STARTING] Proxy is starting...")
start()
