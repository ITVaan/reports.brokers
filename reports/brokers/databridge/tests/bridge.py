# -*- coding: utf-8 -*-

import unittest
import os

from reports.brokers.databridge.tests.utils import custom_sleep
from requests import RequestException

from mock import patch, MagicMock
from restkit import RequestError, ResourceError

from gevent.pywsgi import WSGIServer
from bottle import Bottle, response, request

from reports.brokers.databridge.bridge import DataBridge
from openprocurement_client.client import TendersClientSync, TendersClient
from reports.brokers.databridge.utils import check_412

config = {
    'main':
        {
            'tenders_api_server': 'http://127.0.0.1:20604',
            'tenders_api_version': '0',
            'public_tenders_api_server': 'http://127.0.0.1:20605',
            'buffers_size': 450,
            'full_stack_sync_delay': 15,
            'empty_stack_sync_delay': 101,
            'on_error_sleep_delay': 5,
            'api_token': "api_token"
        }
}


class AlmostAlwaysTrue(object):
    def __init__(self, total_iterations=1):
        self.total_iterations = total_iterations
        self.current_iteration = 0

    def __nonzero__(self):
        if self.current_iteration < self.total_iterations:
            self.current_iteration += 1
            return bool(1)
        return bool(0)


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

    @classmethod
    def tearDownClass(cls):
        cls.api_server.close()
        cls.public_api_server.close()


def setup_routing(app, func, path='/api/0/spore', method='GET'):
    app.route(path, method, func)


def response_spore():
    response.set_cookie("SERVER_ID", ("a7afc9b1fc79e640f2487ba48243ca071c07a823d27"
                                      "8cf9b7adf0fae467a524747e3c6c6973262130fac2b"
                                      "96a11693fa8bd38623e4daee121f60b4301aef012c"))
    return response


class TestBridgeWorker(BaseServersTest):
    def setUp(self):
        self.worker = DataBridge(config)

    def tearDown(self):
        del self.worker

    def test_init(self):
        self.assertEqual(self.worker.delay, 15)
        self.assertEqual(self.worker.sleep_change_value.time_between_requests, 0)

        # check clients
        self.assertTrue(isinstance(self.worker.tenders_sync_client, TendersClientSync))
        self.assertTrue(isinstance(self.worker.client, TendersClient))
        self.assertFalse(self.worker.initialization_event.is_set())

    @patch('reports.brokers.databridge.bridge.TendersClientSync')
    @patch('reports.brokers.databridge.bridge.TendersClient')
    def test_tender_sync_clients(self, sync_client, client):
        self.worker = DataBridge(config)

        # check client config
        self.assertEqual(client.call_args[0], ('',))
        self.assertEqual(client.call_args[1], {'host_url': config['main']['public_tenders_api_server'],
                                               'api_version': config['main']['tenders_api_version']})

        # check sync client config
        self.assertEqual(sync_client.call_args[0], (config['main']['api_token'],))
        self.assertEqual(sync_client.call_args[1],
                         {'host_url': config['main']['tenders_api_server'],
                          'api_version': config['main']['tenders_api_version']})

    def test_start_jobs(self):
        scanner, base_integration = [MagicMock(return_value=i) for i in range(2)]
        self.worker.scanner = scanner
        self.worker.base_integration = base_integration

        self.worker._start_jobs()
        # check that all jobs were started
        self.assertTrue(scanner.called)
        self.assertTrue(base_integration.called)

        self.assertEqual(self.worker.jobs['scanner'], 0)
        self.assertEqual(self.worker.jobs['base_integration'], 1)

    @patch('gevent.sleep')
    def test_run(self, sleep):
        self.worker = DataBridge(config)
        # create mocks
        scanner, base_integration = [MagicMock() for i in range(2)]
        self.worker.scanner = scanner
        self.worker.base_integration = base_integration
        with patch('__builtin__.True', AlmostAlwaysTrue(100)):
            self.worker.run()
        print
        self.assertEqual(self.worker.scanner.call_count, 2)
        self.assertEqual(self.worker.base_integration.call_count, 2)

    def test_openprocurement_api_failure(self):
        self.api_server.stop()
        with self.assertRaises(RequestError):
            self.worker.check_openprocurement_api()
        self.api_server.start()
        self.assertTrue(self.worker.check_openprocurement_api())

    def test_openprocurement_api_mock(self):
        self.worker.client = MagicMock(head=MagicMock(side_effect=RequestError()))
        with self.assertRaises(RequestError):
            self.worker.check_openprocurement_api()
        self.worker.client = MagicMock()
        self.assertTrue(self.worker.check_openprocurement_api())

    def test_check_services(self):
        self.worker.services_not_available = MagicMock(set=MagicMock(), clear=MagicMock())
        self.worker.check_services()
        self.assertFalse(self.worker.services_not_available.clear.called)
        self.worker.check_services()
        self.assertTrue(self.worker.services_not_available.set.called)

    def test_check_services_mock(self):
        self.worker.check_openprocurement_api = MagicMock()
        self.worker.set_wake_up = MagicMock()
        self.worker.set_sleep = MagicMock()
        self.worker.check_services()
        self.assertTrue(self.worker.set_wake_up.called)
        self.worker.check_services()
        self.assertFalse(self.worker.set_sleep.called)

    @patch("gevent.sleep")
    def test_check_log(self, gevent_sleep):
        gevent_sleep = custom_sleep
        self.worker.filtered_tender_ids_queue = MagicMock(qsize=MagicMock(side_effect=Exception()))
        self.worker.check_services = MagicMock(return_value=True)
        self.worker.run()
        self.assertTrue(self.worker.filtered_tender_ids_queue.qsize.called)
