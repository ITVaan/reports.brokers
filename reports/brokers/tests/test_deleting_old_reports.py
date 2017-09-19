# -*- coding: utf-8 -*-
from gevent import event, monkey

monkey.patch_all()

from datetime import datetime
from mock import patch
from time import sleep
from os import path, listdir
from unittest import TestCase
from reports.brokers.databridge.deleting_old_reports import ReportCleaner
from reports.brokers.tests.utils import custom_sleep, test_config


class TestReportsDeleting(TestCase):
    def setUp(self):
        self.sna = event.Event()
        self.sna.set()

    def test_init(self):
        worker = ReportCleaner.spawn(self.sna, "reports_finished_reports")
        self.assertEqual(worker.services_not_available, self.sna)
        self.assertEqual(worker.result_dir, "reports_finished_reports")
        self.assertGreater(datetime.now().isoformat(), worker.start_time.isoformat())
        worker.shutdown()
        del worker

    @patch('gevent.sleep')
    def test_deleting(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        result_dir = test_config.get('result_dir')
        result_file = path.join(result_dir, '2017-08-05-17-00-00_report_number_1.xlsx')
        open(result_file, 'a').close()
        worker = ReportCleaner.spawn(self.sna, result_dir)
        sleep(1)
        self.assertFalse([i for i in listdir(result_dir) if path.splitext(i)[1] == '.xlsx'])
        worker.shutdown()
        del worker
