# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

import os
import requests_mock
import unittest
import hypothesis.strategies as st

from reports.brokers.databridge.utils import EdrDocument
from gevent.queue import Queue
from mock import MagicMock
from time import sleep
from hypothesis import given, assume
from yaml import dump as yaml_dump, load as load_yaml

from utils import AlmostAlwaysFalse
from reports.brokers.databridge.doc_service_client import DocServiceClient
from reports.brokers.databridge.download_from_doc_service import DownloadFromDocServiceWorker

test_document = st.one_of(st.fixed_dictionaries({
    "errors": st.fixed_dictionaries({
        "error": st.just("Couldn't find this code in EDR.")
    }),
    "meta": st.fixed_dictionaries({
        "sourceDate": st.datetimes().map(lambda x: x.isoformat())
    })
}),
    st.fixed_dictionaries({
        "data": st.fixed_dictionaries({
            "registrationStatus": st.just("registered")
        }),
        "meta": st.fixed_dictionaries({
            "sourceDate": st.datetimes()
        })
    }))


class TestDownloadFromDocServiceWorker(unittest.TestCase):
    def setUp(self):
        self.in_queue = Queue(100)
        self.out_queue = Queue(100)

    def execute_example(self, f):
        self.in_queue = Queue(100)
        self.out_queue = Queue(100)
        return f()


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

    @given(st.uuids(), st.uuids(), st.text(), test_document)
    def test_get_items_from_doc_service(self, tender_id, bid_id, doc_url, test_doc):
        assume(doc_url != '')
        res = yaml_dump(test_doc)
        doc_client_mock = MagicMock(download=MagicMock(return_value=res))
        data = EdrDocument(tender_id, bid_id, "111", "UA-EDR", doc_url)
        self.in_queue.put(data)
        worker = DownloadFromDocServiceWorker(MagicMock(), doc_client_mock, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.get_item_from_doc_service()
        result = worker.edr_data_to_database.get()
        self.assertEqual(result.identifier, "111")
        self.assertEqual(result.scheme, "UA-EDR")
        self.assertEqual(result.edr_status,
                         1 if test_doc.get('data') and test_doc.get('data').get('registrationStatus') else 0)
        self.assertEqual(result.edr_date, test_doc.get('meta').get('sourceDate'))

    @given(st.uuids(), st.uuids(), st.text(), test_document)
    def test_retry_get_items_from_doc_service(self, tender_id, bid_id, doc_url, test_doc):
        assume(doc_url != '')
        res = yaml_dump(test_doc)
        data = EdrDocument(tender_id, bid_id, "111", "UA-EDR", doc_url)
        doc_client_mock = MagicMock(download=MagicMock(return_value=res))
        worker = DownloadFromDocServiceWorker(MagicMock(), doc_client_mock, self.in_queue, self.out_queue)
        worker.retry_items_to_download_queue.put(data)
        worker.exit = AlmostAlwaysFalse()
        worker.retry_get_item_from_doc_service()
        result = worker.edr_data_to_database.get()
        self.assertEqual(result.identifier, "111")
        self.assertEqual(result.scheme, "UA-EDR")
        self.assertEqual(result.edr_status,
                         1 if test_doc.get('data') and test_doc.get('data').get('registrationStatus') else 0)
        self.assertEqual(result.edr_date, test_doc.get('meta').get('sourceDate'))
        # TODO this test will have to be updated after I finish interaction with DB

    @requests_mock.Mocker()
    def test_sent_get_request(self, mrequest):
        url = '{host}:{port}/get/111'.format(host="127.0.0.1", port=6555)
        with open(os.path.join(os.path.dirname(__file__), "test_edr_data.yaml"), mode='r') as f:
            content = f.read()
            mrequest.get(url, [{'text': content, 'status_code': 200}])
        content = load_yaml(content)
        data = EdrDocument(1, 1, "111", "UA-EDR", "127.0.0.1:6555/get/111")
        self.in_queue.put(data)
        client = DocServiceClient(host="127.0.0.1")
        worker = DownloadFromDocServiceWorker(MagicMock(), client, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.get_item_from_doc_service()
        self.assertEqual(len(mrequest.request_history), 1)
        result = worker.edr_data_to_database.get()
        self.assertEqual(result.identifier, "111")
        self.assertEqual(result.scheme, "UA-EDR")
        self.assertEqual(result.edr_status,
                         1 if content.get('data') and content.get('data').get('registrationStatus') else 0)
        self.assertEqual(result.edr_date, content.get('meta').get('sourceDate'))

    @requests_mock.Mocker()
    def test_sent_get_request_fail_and_sux(self, mrequest):
        url = '{host}:{port}/get/111'.format(host="127.0.0.1", port=6555)
        content = str(test_document.example())
        mrequest.get(url, [{'status_code': 404}, {'text': content, 'status_code': 200}])
        content = load_yaml(content)
        data = EdrDocument(1, 1, "111", "UA-EDR", url)
        self.in_queue.put(data)
        client = DocServiceClient(host="127.0.0.1")
        worker = DownloadFromDocServiceWorker(MagicMock(), client, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.temp_action()
        result = worker.edr_data_to_database.get()
        self.assertEqual(len(mrequest.request_history), 2)
        self.assertEqual(result.identifier, "111")
        self.assertEqual(result.scheme, "UA-EDR")
        self.assertEqual(result.edr_status,
                         1 if content.get('data') and content.get('data').get('registrationStatus') else 0)
        self.assertEqual(result.edr_date, content.get('meta').get('sourceDate'))

    @requests_mock.Mocker()
    def test_sent_get_request_exception(self, mrequest):
        url = '{host}:{port}/get/111'.format(host="127.0.0.1", port=6555)
        mrequest.get(url, [{'status_code': 404} for _ in range(6)])
        data = EdrDocument(1, 1, "111", "UA-EDR", "127.0.0.1:6555/get/111")
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
        content = str(test_document.example())
        mrequest.get(url, [{'status_code': 404} for _ in range(6)] + [{'text': content, 'status_code': 200}])
        content = load_yaml(content)
        data = EdrDocument(1, 1, "111", "UA-EDR", url)
        self.in_queue.put(data)
        client = DocServiceClient(host="127.0.0.1")
        worker = DownloadFromDocServiceWorker(MagicMock(), client, self.in_queue, self.out_queue)
        worker.exit = AlmostAlwaysFalse()
        worker.temp_action()
        worker.retry_temp_action()
        result = worker.edr_data_to_database.get()
        self.assertEqual(len(mrequest.request_history), 7)
        self.assertEqual(result.identifier, "111")
        self.assertEqual(result.scheme, "UA-EDR")
        self.assertEqual(result.edr_status,
                         1 if content.get('data') and content.get('data').get('registrationStatus') else 0)
        self.assertEqual(result.edr_date, content.get('meta').get('sourceDate'))
