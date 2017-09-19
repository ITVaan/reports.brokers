# -*- coding: utf-8 -*-
from time import sleep

from gevent import monkey

monkey.patch_all()
from gevent import killall
from mock import MagicMock, patch
from openprocurement_client.client import TendersClient, TendersClientSync
from restkit import RequestError
from reports.brokers.databridge.bridge import DataBridge
from reports.brokers.tests.test_databridge.base import BaseServersTest
from reports.brokers.tests.utils import config, config_get
from utils import AlmostAlwaysTrue, custom_sleep


class TestBridgeWorker(BaseServersTest):
    def setUp(self):
        self.worker = DataBridge(config)

    def test_init(self):
        self.assertEqual(self.worker.database, config_get('database'))
        self.assertEqual(self.worker.delay, config_get('delay'))
        self.assertEqual(self.worker.sleep_change_value.time_between_requests, 0)
        self.assertTrue(isinstance(self.worker.tenders_sync_client, TendersClientSync))
        self.assertTrue(isinstance(self.worker.client, TendersClient))
        self.assertFalse(self.worker.initialization_event.is_set())

    @patch('reports.brokers.databridge.bridge.TendersClientSync')
    @patch('reports.brokers.databridge.bridge.TendersClient')
    def test_tender_sync_clients(self, sync_client, client):
        self.worker = DataBridge(config)
        # check client config
        self.assertEqual(client.call_args[0], ('',))
        self.assertEqual(client.call_args[1], {'host_url': config_get('public_tenders_api_server'),
                                               'api_version': config_get('tenders_api_version')})

        # check sync client config
        self.assertEqual(sync_client.call_args[0], (config_get('api_token'),))
        self.assertEqual(sync_client.call_args[1],
                         {'host_url': config_get('tenders_api_server'),
                          'api_version': config_get('tenders_api_version')})

    def test_start_jobs(self):
        scanner, base_integration, report_cleaner = [MagicMock(return_value=i) for i in range(3)]
        self.worker.scanner = scanner
        self.worker.base_integration = base_integration
        self.worker.report_cleaner = report_cleaner

        self.worker._start_jobs()
        # check that all jobs were started
        self.assertTrue(scanner.called)
        self.assertTrue(base_integration.called)
        self.assertTrue(report_cleaner.called)

        self.assertEqual(self.worker.jobs['Scanner'], 0)
        self.assertEqual(self.worker.jobs['BaseIntegration'], 1)
        self.assertEqual(self.worker.jobs['ReportCleaner'], 2)

    @patch('gevent.sleep')
    def test_bridge_run(self, sleep):
        # create mocks
        scanner, base_integration = [MagicMock() for i in range(2)]
        self.worker.scanner = scanner
        self.worker.base_integration = base_integration
        with patch('__builtin__.True', AlmostAlwaysTrue()):
            self.worker.run()
        self.assertEqual(self.worker.scanner.call_count, 1)
        self.assertEqual(self.worker.base_integration.call_count, 1)

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

    @patch("gevent.sleep")
    def test_check_services_exception(self, gevent_sleep):
        self.worker.client = MagicMock(head=MagicMock(side_effect=RequestError()))
        self.assertRaises(RequestError, lambda: self.worker.check_openprocurement_api())
        self.worker.all_available()
        self.assertFalse(self.worker.all_available())
        self.worker.check_services()
        self.assertTrue(self.worker.set_sleep)


    def test_check_services_mock(self):
        self.worker.check_openprocurement_api = MagicMock()
        self.worker.set_wake_up = MagicMock()
        self.worker.set_sleep = MagicMock()
        self.worker.check_services()
        self.assertTrue(self.worker.set_wake_up.called)
        self.worker.check_services()
        self.assertFalse(self.worker.set_sleep.called)

    @patch("gevent.sleep")
    def test_check_log_filtered_tender_ids_queue(self, gevent_sleep):
        gevent_sleep = custom_sleep
        self.worker.filtered_tender_ids_queue = MagicMock(qsize=MagicMock(side_effect=Exception()))
        self.worker.check_services = MagicMock(return_value=True)
        self.worker.run()
        self.assertTrue(self.worker.filtered_tender_ids_queue.qsize.called)

    @patch("gevent.sleep")
    def test_check_log_processing_docs_queue(self, gevent_sleep):
        gevent_sleep = custom_sleep
        self.worker.processing_docs_queue = MagicMock(qsize=MagicMock(side_effect=Exception()))
        self.worker.check_services = MagicMock(return_value=True)
        self.worker.run()
        self.assertTrue(self.worker.processing_docs_queue.qsize.called)

    @patch("gevent.sleep")
    def test_launch(self, gevent_sleep):
        self.worker.all_available = MagicMock(return_value=True)
        with patch('__builtin__.True', AlmostAlwaysTrue()):
            self.worker.launch()
        gevent_sleep.assert_not_called()

    @patch("gevent.sleep")
    def test_launch_unavailable(self, gevent_sleep):
        self.worker.all_available = MagicMock(return_value=False)
        with patch('__builtin__.True', AlmostAlwaysTrue()):
            self.worker.launch()
        self.assertFalse(gevent_sleep.called)

    def test_revive_job(self):
        self.worker._start_jobs()
        self.assertEqual(self.worker.jobs['Scanner'].dead, False)
        killall(self.worker.jobs.values(), timeout=1)
        self.assertEqual(self.worker.jobs['Scanner'].dead, True)
        self.worker.revive_job('scanner')
        self.assertEqual(self.worker.jobs['scanner'].dead, False)
        killall(self.worker.jobs.values())

    def test_check_and_revive_jobs(self):
        self.worker.jobs = {"test": MagicMock(dead=MagicMock(return_value=True))}
        self.worker.revive_job = MagicMock()
        self.worker.check_and_revive_jobs()
        self.worker.revive_job.assert_called_once_with("test")
