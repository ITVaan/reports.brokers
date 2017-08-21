# -*- coding: utf-8 -*-
from gevent import sleep as gsleep
from uuid import uuid4
from json import dumps


def custom_sleep(seconds=0):
    return gsleep(seconds=0)


def generate_request_id():
    return 'req-{}'.format(uuid4().hex)


class ResponseMock(object):
    def __init__(self, headers, data, status_int=200):
        self.data = data
        self.headers = headers
        self.status_int = status_int

    def body_string(self):
        return dumps(self.data)

    def next(self):
        pass
