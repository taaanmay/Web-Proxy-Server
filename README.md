# Web-Proxy-Server
Developing a Web-Proxy Server which enables Website Caching, Blocking Features and other functionalities


# Requirements
Project is made to be used in Python 3. 
The Browser's network settings should be set to use the manual proxy with `localhost` as the name and Port Number used is `8080`
(I have been using Firerox as my browser for this project)


# HTTP and HTTPS Requests 
There are 2 types of requests -:
1) HTTP Requests
2) HTTPS Requsts

# Measure Time taken to retrieve a request from Server and Cache
When the first request is made, server retrieves the file and saves it in the cache. When that file is needed again, file in cache is used. Retrieving the file from cache is quite fast as compared to retrieving file from the server.

