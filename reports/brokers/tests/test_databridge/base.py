# -*- coding: utf-8 -*-
import unittest

import os
from bottle import Bottle, response
from gevent.pywsgi import WSGIServer

config = {
    'main':
        {
            'tenders_api_server': 'http://127.0.0.1:20604',
            'tenders_api_version': '2.3',
            'public_tenders_api_server': 'http://127.0.0.1:20605',
            'buffers_size': 450,
            'full_stack_sync_delay': 15,
            'empty_stack_sync_delay': 101,
            'on_error_sleep_delay': 5,
            'api_token': "api_token",
            'db_name': 'reports_data',
            'delay': 1,
        }
}


class BaseServersTest(unittest.TestCase):
    """Api server to test reports.brokers.databridge.bridge """

    relative_to = os.path.dirname(__file__)  # crafty line

    @classmethod
    def setUpClass(cls):
        cls.api_server_bottle = Bottle()
        cls.api_server = WSGIServer(('127.0.0.1', 20604), cls.api_server_bottle, log=None)
        setup_routing(cls.api_server_bottle, response_spore)
        cls.public_api_server = WSGIServer(('127.0.0.1', 20605), cls.api_server_bottle, log=None)

        # start servers
        cls.api_server.start()
        cls.public_api_server.start()

    def tearDown(self):
        del self.worker


def setup_routing(app, func, path='/api/{}/spore'.format(config['main']['tenders_api_version']), method='GET'):
    app.route(path, method, func)


def response_spore():
    response.set_cookie("SERVER_ID", ("a7afc9b1fc79e640f2487ba48243ca071c07a823d27"
                                      "8cf9b7adf0fae467a524747e3c6c6973262130fac2b"
                                      "96a11693fa8bd38623e4daee121f60b4301aef012c"))
    return response
