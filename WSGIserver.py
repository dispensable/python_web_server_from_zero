#_*_coding:utf-8_*_
#!/usr/bin/env python

import socket
import StringIO
import sys
import time


class WSGIServer(object):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # 创建套接字
        listen_socket = socket.socket(self.address_family, self.socket_type)
        self.listen_socket = listen_socket
        # 设置套接字
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定
        listen_socket.bind(server_address)
        # 监听
        listen_socket.listen(self.request_queue_size)
        # 设置套接字属性
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # 设置web应用设置的首部
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def server_forever(self):
        listen_socket = self.listen_socket
        while True:
            self.client_connection, client_address = listen_socket.accept()
            self.handle_one_request()

    def handle_one_request(self):
        # 接收数据
        self.request_data = request_data = self.client_connection.recv(4096)

        print "request data: <------"
        print request_data
        # 解析数据
        self.parse_request(request_data)
        # 使用请求数据构建环境
        env = self.get_environ()
        # 使用应用返回响应
        result = self.application(env, self.start_response)

        # 返回响应到客户端
        self.finish_response(result)

    def parse_request(self, text):
        # 取出报文第一行
        request_line_with_rn = text.splitlines()[0]
        # 去除本行结尾的\r\n
        request_line = request_line_with_rn.rstrip('\r\n')
        # http报头 请求方法, 路径,协议
        (self.request_method, self.path, self.request_version) = request_line.split()

    def get_environ(self):
        env = {}
        # wsgi变量
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multithread'] = False
        env['wsgi.run_once'] = False
        # cgi变量
        env['REQUEST_METHOD'] = self.request_method
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)

        return env

    def start_response(self, status, response_headers, exc_infor=None):
        # server headers
        server_headers = [
            ('Date', time.time()),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            # 构建http头部
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            # 添加主体
            for data in result:
                response += data
            print "response ------->"
            print response
            # 发送报文
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()

SERVER_ADDRESS = (HOST, PORT) = '', 8888


def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('provide a wsgi application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print 'WSGIServer: serving http on port {port} ...\n'.format(port=PORT)
    httpd.server_forever()