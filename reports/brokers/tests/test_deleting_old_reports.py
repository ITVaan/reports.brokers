# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

from datetime import datetime
import os
from mock import patch

from unittest import TestCase
from reports.brokers.api.views.deleting_old_reports import ReportCleaner
from reports.brokers.tests.utils import custom_sleep


class TestReportsDeleting(TestCase):
    def test_init(self):
        worker = ReportCleaner.spawn()
        self.assertGreater(datetime.now().isoformat(), worker.start_time.isoformat())

    @patch('gevent.sleep')
    def test_deleting(self, gevent_sleep):
        gevent_sleep.side_effect = custom_sleep
        result_dir = 'reports/brokers/tests/test_reports'
        result_file = os.path.join(result_dir, '2017-08-05-17-00-00_report-number=1.xlsx')
        open(result_file, 'a').close()
        worker = ReportCleaner.spawn()
        worker.result_dir = result_dir
        worker.join(3)
        self.assertFalse(os.listdir(result_dir))
