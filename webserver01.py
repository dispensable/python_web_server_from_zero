# _*_coding:utf-8_*_
#!/usr/bin/env python

import socket

(HOST, PORT) = '', 8888

socket_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_listen.bind((HOST, PORT))
socket_listen.listen(5)
print 'Serving HTTP on port {0}....'.format(PORT)

while True:
    client_connection, client_address = socket_listen.accept()
    request = client_connection.recv(4096)
    print request

    response = """HTTP/1.1 200 OK

                Hello world!
                """
    print "connection from {0}".format(client_address)
    client_connection.sendall(response)
    client_connection.close()