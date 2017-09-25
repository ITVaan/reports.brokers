# -*- coding: utf-8 -*-
from gevent import event, monkey

monkey.patch_all()

from datetime import datetime
from mock import patch
from time import sleep
from os import path, listdir, remove
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
        for file in listdir(result_dir):
            if path.splitext(file)[1] == '.xlsx':
                remove(path.abspath(path.join(result_dir, file)))
        date = '2017-05-02-13-00-00'
        result_file = path.join(result_dir,
                                '{}_start_date_{}_end_date_{}_report_number_1.xlsx'.format(date, date, date))
        open(result_file, 'a').close()
        worker = ReportCleaner.spawn(self.sna, result_dir)
        sleep(1)
        self.assertFalse([i for i in listdir(result_dir) if path.splitext(i)[1] == '.xlsx'])
        worker.shutdown()
        del worker
