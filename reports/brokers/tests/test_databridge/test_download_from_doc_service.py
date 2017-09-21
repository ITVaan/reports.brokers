# -*- coding: utf-8 -*-
from gevent import monkey
from gevent.hub import LoopExit

from reports.brokers.databridge.doc_service_client import DocServiceClient

monkey.patch_all()

import requests_mock
import unittest
import hypothesis.strategies as st

from reports.brokers.databridge.utils import EdrDocument
from gevent.queue import Queue
from mock import MagicMock
from time import sleep
from hypothesis import given, assume

from utils import AlmostAlwaysFalse
from reports.brokers.databridge.download_from_doc_service import DownloadFromDocServiceWorker


class TestDownloadFromDocServiceWorker(unittest.TestCase):
    def setUp(self):
        self.in_queue = Queue(100)
        self.out_queue = Queue(100)

    @given(st.text())
    def test_init(self, url):
        doc_client_mock = DocServiceClient(url)
        worker = DownloadFromDocServiceWorker(MagicMock(), doc_client_mock, self.in_queue, self.out_queue)
        self.assertEqual(worker.doc_client, doc_client_mock)

    def test_start_jobs(self):
        worker = DownloadFromDocServiceWorker(MagicMock(), MagicMock(), self.in_queue, self.out_queue)
        worker.get_item_from_doc_service = MagicMock()
        worker.retry_get_item_from_doc_service = MagicMock()
        worker._start_jobs()
        sleep(1)
        worker.get_item_from_doc_service.assert_called_once()
        worker.retry_get_item_from_doc_service.assert_called_once()

    @given(st.text(), st.text(), st.text())
    def test_get_items_from_doc_service(self, tender_id, bid_id, doc_url):
        data = EdrDocument(tender_id, bid_id, doc_url)
        self.in_queue.put(data)
        worker = DownloadFromDocServiceWorker(MagicMock(), MagicMock(), self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.get_item_from_doc_service()

    @given(st.text(), st.text(), st.text())
    def test_retry_get_items_from_doc_service(self, tender_id, bid_id, doc_url):
        assume(doc_url != '')
        data = EdrDocument(tender_id, bid_id, doc_url)
        worker = DownloadFromDocServiceWorker(MagicMock(), MagicMock(), self.in_queue, self.out_queue)
        worker.retry_items_to_download_queue.put(data)
        worker.exit = AlmostAlwaysFalse()
        worker.retry_get_item_from_doc_service()
        self.assertEqual(worker.retry_items_to_download_queue.peek(), (tender_id, bid_id, doc_url))
        #TODO this test will have to be updated after I finish interaction with DB

    @requests_mock.Mocker()
    def test_sent_get_request(self, mrequest):
        url = '{host}:{port}/get/111'.format(host="127.0.0.1", port=6555)
        mrequest.get(url, [{'json': {'data': {}}, 'status_code': 200}])
        data = EdrDocument(1, 1, "127.0.0.1:6555/get/111")
        self.in_queue.put(data)
        client = DocServiceClient(host="127.0.0.1")
        worker = DownloadFromDocServiceWorker(MagicMock(), client, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.get_item_from_doc_service()
        self.assertEqual(len(mrequest.request_history), 1)
        self.assertEqual(self.out_queue.get(), (data.tender_id, data.bid_id, {'data': {}}))

    @requests_mock.Mocker()
    def test_sent_get_request_fail_and_sux(self, mrequest):
        url = '{host}:{port}/get/111'.format(host="127.0.0.1", port=6555)
        mrequest.get(url, [{'status_code': 404}, {'json': {'data': {}}, 'status_code': 200}])
        data = EdrDocument(1, 1, url)
        self.in_queue.put(data)
        client = DocServiceClient(host="127.0.0.1")
        worker = DownloadFromDocServiceWorker(MagicMock(), client, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.temp_action()
        self.assertEqual(len(mrequest.request_history), 2)
        self.assertEqual(self.out_queue.get(), (data.tender_id, data.bid_id, {'data': {}}))

    @requests_mock.Mocker()
    def test_sent_get_request_exception(self, mrequest):
        url = '{host}:{port}/get/111'.format(host="127.0.0.1", port=6555)
        mrequest.get(url, [{'status_code': 404} for _ in range(6)])
        data = EdrDocument(1, 1, "127.0.0.1:6555/get/111")
        self.in_queue.put(data)
        client = DocServiceClient(host="127.0.0.1")
        worker = DownloadFromDocServiceWorker(MagicMock(), client, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.get_item_from_doc_service()
        self.assertEqual(len(mrequest.request_history), 5)
        self.assertEqual(self.out_queue.qsize(), 0)

    @requests_mock.Mocker()
    def test_retry_sent_get_request_exception(self, mrequest):
        url = '{host}:{port}/get/111'.format(host="127.0.0.1", port=6555)
        mrequest.get(url, [{'status_code': 404} for _ in range(6)] + [{'json': {'data': {}}, 'status_code': 200}])
        data = EdrDocument(1, 1, url)
        self.in_queue.put(data)
        client = DocServiceClient(host="127.0.0.1")
        worker = DownloadFromDocServiceWorker(MagicMock(), client, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.temp_action()
        worker.retry_temp_action()
        self.assertEqual(len(mrequest.request_history), 7)
        self.assertEqual(self.out_queue.get(), (data.tender_id, data.bid_id, {'data': {}}))
