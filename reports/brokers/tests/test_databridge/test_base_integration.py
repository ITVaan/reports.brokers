# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

import uuid
import unittest
import datetime

from bottle import Bottle
from time import sleep
from gevent.pywsgi import WSGIServer
from gevent.queue import Queue
from mock import MagicMock, patch
from bottle import response
from simplejson import dumps
from gevent import event
from reports.brokers.tests.utils import custom_sleep
from restkit.errors import ResourceError
from reports.brokers.databridge.base_integration import BaseIntegration
from reports.brokers.databridge.bridge import TendersClientSync
from reports.brokers.tests.utils import config_get
from reports.brokers.utils import get_root_pwd
from utils import generate_request_id
from reports.brokers.databridge.sleep_change_value import APIRateController

SERVER_RESPONSE_FLAG = 0
SPORE_COOKIES = ("a7afc9b1fc79e640f2487ba48243ca071c07a823d27"
                 "8cf9b7adf0fae467a524747e3c6c6973262130fac2b"
                 "96a11693fa8bd38623e4daee121f60b4301aef012c")
COOKIES_412 = ("b7afc9b1fc79e640f2487ba48243ca071c07a823d27"
               "8cf9b7adf0fae467a524747e3c6c6973262130fac2b"
               "96a11693fa8bd38623e4daee121f60b4301aef012c")
CODES = ('14360570', '0013823', '23494714')


def setup_routing(app, func, path='/api/2.3/spore', method='GET'):
    app.route(path, method, func)


def response_spore():
    response.set_cookie("SERVER_ID", SPORE_COOKIES)
    return response


def response_412():
    response.status = 412
    response.set_cookie("SERVER_ID", COOKIES_412)
    return response


def response_get_tender():
    response.status = 200
    response.headers['X-Request-ID'] = '125'
    return dumps({'prev_page': {'offset': '123'},
                  'next_page': {'offset': '1234'},
                  'data': {'status': "active.pre-qualification",
                           'id': '123',
                           'procurementMethodType': 'aboveThresholdEU',
                           'awards': [{'id': '124',
                                       'bid_id': '111',
                                       'status': 'pending',
                                       'suppliers': [{'identifier': {
                                           'scheme': 'UA-EDR',
                                           'id': CODES[0]}}]}]}})


def generate_response():
    global SERVER_RESPONSE_FLAG
    if SERVER_RESPONSE_FLAG == 0:
        SERVER_RESPONSE_FLAG = 1
        return response_412()
    return response_get_tender()


class TestBaseIntegrationWorker(unittest.TestCase):
    def setUp(self):
        self.filtered_tender_ids_queue = Queue(10)
        self.processing_docs_queue = Queue(10)
        self.tender_id = uuid.uuid4().hex
        self.filtered_tender_ids_queue.put(self.tender_id)
        self.sleep_change_value = APIRateController()
        self.client = MagicMock()
        self.sna = event.Event()
        self.sna.set()
        self.worker = BaseIntegration.spawn(self.client, self.filtered_tender_ids_queue, self.processing_docs_queue,
                                            self.sna, self.sleep_change_value,
                                            db_host=config_get("db_host"),
                                            db_user=config_get("db_user"),
                                            db_password=get_root_pwd(),
                                            database=config_get("database"),
                                            db_charset=config_get("db_charset"))
        self.bid_ids = [uuid.uuid4().hex for _ in range(5)]
        self.qualification_ids = [uuid.uuid4().hex for _ in range(5)]
        self.award_ids = [uuid.uuid4().hex for _ in range(5)]
        self.request_ids = [generate_request_id() for _ in range(2)]

    def tearDown(self):
        self.worker.shutdown()
        del self.worker

    def test_init(self):
        worker = BaseIntegration.spawn(None, None, None, self.sna, self.sleep_change_value,
                                       db_host=config_get("db_host"),
                                       db_user=config_get("db_user"),
                                       db_password=get_root_pwd(),
                                       database=config_get("database"),
                                       db_charset=config_get("db_charset"))
        self.assertGreater(datetime.datetime.now().isoformat(), worker.start_time.isoformat())
        self.assertEqual(worker.tenders_sync_client, None)
        self.assertEqual(worker.filtered_tender_ids_queue, None)
        self.assertEqual(worker.processing_docs_queue, None)
        self.assertEqual(worker.services_not_available, self.sna)
        self.assertEqual(worker.sleep_change_value.time_between_requests, 0)
        self.assertEqual(worker.database, config_get("database"))
        self.assertEqual(worker.delay, 15)
        self.assertEqual(worker.exit, False)
        worker.shutdown()
        del worker

    @patch('gevent.sleep')
    def test_adding_tenders_to_queue(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        api_server_bottle = Bottle()
        api_server = WSGIServer(('127.0.0.1', 20604), api_server_bottle, log=None)
        setup_routing(api_server_bottle, response_spore)
        setup_routing(api_server_bottle, generate_response, path='/api/2.3/tenders/{}'.format(self.tender_id))
        api_server.start()
        client = TendersClientSync('', host_url='http://127.0.0.1:20604', api_version='2.3')
        self.assertEqual(client.headers['Cookie'], 'SERVER_ID={}'.format(SPORE_COOKIES))
        api_server.stop()

    @patch('gevent.sleep')
    def test_get_tender_429(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        self.client.request = MagicMock(side_effect=ResourceError(http_code=429))
        self.sleep_change_value.increment_step = 2
        self.sleep_change_value.decrement_step = 1
        sleep(1)
        self.assertEqual(self.worker.sleep_change_value.time_between_requests, 2)
        gevent_sleep.assert_called_with(15)
        self.assertEqual(self.filtered_tender_ids_queue.qsize(), 0)
        self.assertEqual(self.processing_docs_queue.qsize(), 0)

    @patch('gevent.sleep')
    def test_get_tender(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        self.client.request = MagicMock(side_effect=ResourceError())
        sleep(1)
        self.assertEqual(self.worker.sleep_change_value.time_between_requests, 0)
        gevent_sleep.assert_called_with(15)
        self.assertEqual(self.filtered_tender_ids_queue.qsize(), 0)
        self.assertEqual(self.processing_docs_queue.qsize(), 0)

    @patch('gevent.sleep')
    def test_get_tender_exception(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        self.client.request = MagicMock(side_effect=Exception())
        sleep(1)
        self.assertEqual(self.worker.sleep_change_value.time_between_requests, 0)
        gevent_sleep.assert_called_with(15)
        self.assertEqual(self.filtered_tender_ids_queue.qsize(), 0)
        self.assertEqual(self.processing_docs_queue.qsize(), 0)

    @patch('gevent.sleep')
    def test_processing_docs(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        api_server_bottle = Bottle()
        api_server = WSGIServer(('127.0.0.1', 20604), api_server_bottle, log=None)
        setup_routing(api_server_bottle, response_spore)
        setup_routing(api_server_bottle, generate_response, path='/api/2.3/tenders/{}'.format(self.tender_id))
        api_server.start()
        client = TendersClientSync('', host_url='http://127.0.0.1:20604', api_version='2.3')
        self.assertEqual(client.headers['Cookie'], 'SERVER_ID={}'.format(SPORE_COOKIES))
        api_server.stop()
