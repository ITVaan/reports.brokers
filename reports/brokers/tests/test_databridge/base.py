# -*- coding: utf-8 -*-
import unittest
from ConfigParser import SafeConfigParser

from bottle import Bottle, response
from gevent.pywsgi import WSGIServer
from os import path

from reports.brokers.tests.utils import config_get, config
from reports.brokers.utils import get_root_pwd

class BaseServersTest(unittest.TestCase):
    """Api server to test reports.brokers.databridge.bridge """

    relative_to = path.dirname(__file__)  # crafty line

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


def setup_routing(app, func, path='/api/{}/spore'.format(config_get('tenders_api_version')), method='GET'):
    app.route(path, method, func)


def response_spore():
    response.set_cookie("SERVER_ID", ("a7afc9b1fc79e640f2487ba48243ca071c07a823d27"
                                      "8cf9b7adf0fae467a524747e3c6c6973262130fac2b"
                                      "96a11693fa8bd38623e4daee121f60b4301aef012c"))
    return response
