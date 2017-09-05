# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

import uuid
import unittest
import datetime

from gevent.queue import Queue
from mock import MagicMock
from munch import munchify
from bottle import response
from simplejson import dumps
from gevent import event

from reports.brokers.databridge.base_integration import BaseIntegration
from reports.brokers.tests.test_databridge.utils import generate_request_id, ResponseMock
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
        self.tender_id = uuid.uuid4().hex
        self.filtered_tender_ids_queue.put(self.tender_id)
        self.sleep_change_value = APIRateController()
        self.client = MagicMock()
        self.sna = event.Event()
        self.sna.set()
        self.worker = BaseIntegration.spawn(self.client, self.filtered_tender_ids_queue, self.sna,
                                            self.sleep_change_value)
        self.bid_ids = [uuid.uuid4().hex for _ in range(5)]
        self.qualification_ids = [uuid.uuid4().hex for _ in range(5)]
        self.award_ids = [uuid.uuid4().hex for _ in range(5)]
        self.request_ids = [generate_request_id() for _ in range(2)]
        self.response = ResponseMock({'X-Request-ID': self.request_ids[0]},
                                     munchify({'prev_page': {'offset': '123'},
                                               'next_page': {'offset': '1234'},
                                               'data': {'status': "active.pre-qualification",
                                                        'id': self.tender_id,
                                                        'procurementMethodType': 'aboveThresholdEU',
                                                        'awards': [self.awards(0, 0, 'pending', CODES[0])]}}))

    def tearDown(self):
        self.worker.shutdown()
        del self.worker

    def awards(self, counter_id, counter_bid_id, status, sup_id):
        return {'id': self.award_ids[counter_id], 'bid_id': self.bid_ids[counter_bid_id], 'status': status,
                'suppliers': [{'identifier': {'scheme': 'UA-EDR', 'id': sup_id}}]}

    def bids(self, counter_id, edr_id):
        return {'id': self.bid_ids[counter_id], 'tenderers': [{'identifier': {'scheme': 'UA-EDR', 'id': edr_id}}]}

    def qualifications(self, status, counter_qual_id, counter_bid_id):
        return {'status': status, 'id': self.qualification_ids[counter_qual_id], 'bidID': self.bid_ids[counter_bid_id]}

    def check_data_objects(self, obj, example):
        """Checks that two data objects are equal,
                  that Data.file_content.meta.id is not none
         """
        self.assertEqual(obj.tender_id, example.tender_id)
        self.assertEqual(obj.item_id, example.item_id)
        self.assertEqual(obj.code, example.code)
        self.assertEqual(obj.item_name, example.item_name)
        self.assertIsNotNone(obj.file_content['meta']['id'])
        self.assertEqual(obj.file_content['meta']['sourceRequests'], example.file_content['meta']['sourceRequests'])

    def test_init(self):
        worker = BaseIntegration.spawn(None, None, self.sna, self.sleep_change_value)
        self.assertGreater(datetime.datetime.now().isoformat(), worker.start_time.isoformat())
        self.assertEqual(worker.tenders_sync_client, None)
        self.assertEqual(worker.filtered_tender_ids_queue, None)
        self.assertEqual(worker.services_not_available, self.sna)
        self.assertEqual(worker.sleep_change_value.time_between_requests, 0)
        self.assertEqual(worker.delay, 15)
        self.assertEqual(worker.exit, False)
        worker.shutdown()
        del worker
