# -*- coding: utf-8 -*-
from gevent import monkey, spawn, event

monkey.patch_all()

import os
from datetime import datetime
from mock import patch
from time import sleep
from unittest import TestCase
from reports.brokers.api.views.deleting_old_reports import ReportCleaner
from reports.brokers.tests.utils import custom_sleep


class TestReportsDeleting(TestCase):
    def setUp(self):
        self.sna = event.Event()
        self.sna.set()

    def test_init(self):
        worker = ReportCleaner.spawn(self.sna)
        self.assertEqual(worker.services_not_available, self.sna)
        self.assertGreater(datetime.now().isoformat(), worker.start_time.isoformat())
        worker.shutdown()
        del worker

    @patch('gevent.sleep')
    def test_deleting(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        result_dir = 'reports/brokers/tests/test_reports'
        result_file = os.path.join(result_dir, '2017-08-05-17-00-00_report-number=1.xlsx')
        open(result_file, 'a').close()
        worker = ReportCleaner.spawn(self.sna)
        worker.result_dir = result_dir
        sleep(1)
        self.assertFalse(os.listdir(result_dir))
        worker.shutdown()
        del worker
