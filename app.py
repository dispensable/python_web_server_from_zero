# _*_coding:utf-8_*_
# !/usr/bin/env python


def app(environ, start_response):
    status = '200 ok'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world from a simple WSGI application!\n']