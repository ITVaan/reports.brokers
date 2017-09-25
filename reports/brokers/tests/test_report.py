from hashlib import sha256

from os import path

from pyramid import testing
from reports.brokers.api.views.report import ReportView
from reports.brokers.tests.base_db_test import BaseDbTestCase
from reports.brokers.tests.utils import test_config


class TestReport(BaseDbTestCase):
    def test_init(self):
        request = testing.DummyRequest()
        setattr(request.registry, 'settings', test_config)
        rv = ReportView(request)
        self.assertEqual(rv.request, request)

    def test_generate(self):
        request = testing.DummyRequest()
        setattr(request.registry, 'settings', test_config)
        cursor = self.conn.cursor(buffered=True)
        password = sha256("test").hexdigest()
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("test", "{}", 0);""".format(
            password))
        cursor.close()
        self.conn.commit()
        data = {
            'start_report_period': '01.05.2017',
            'end_report_period': '01.06.2017',
            'report_number': '1',
            'user_name': 'test',
            'password': 'test',
            'config': test_config}
        setattr(request, 'GET', data)
        rv = ReportView(request)
        self.assertEqual(rv.generate().status_int, 200)

    def test_file_exist(self):
        request = testing.DummyRequest()
        setattr(request.registry, 'settings', test_config)
        result_dir = test_config.get('result_dir')
        date = '2017-05-02-00-00-00'
        start_date = '2017-05-01-00-00-00'
        end_date = '2017-06-01-00-00-00'
        result_file = path.join(result_dir,
                                '{}_start_date_{}_end_date_{}_report_number_1.xlsx'.format(date, start_date, end_date))
        open(result_file, 'a').close()
        data = {
            'start_report_period': '01.05.2017',
            'end_report_period': '01.06.2017',
            'report_number': '1',
            'user_name': 'test',
            'password': 'test',
            'config': test_config}
        setattr(request, 'GET', data)
        rv = ReportView(request)
        self.assertEqual(rv.generate().status_int, 200)
