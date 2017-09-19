from unittest import TestCase
from pyramid import testing
from reports.brokers.tests.utils import test_config
from reports.brokers.api.views.report import ReportView


class TestReport(TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        setattr(self.request.registry, 'settings', test_config)
        self.rv = ReportView(self.request)

    def test_init(self):
        self.assertEqual(self.rv.request, self.request)

    def test_generate(self):
        test_config['database'] = 'reports_data'
        data = {
            'start_report_period': '01.05.2017',
            'end_report_period': '01.06.2017',
            'report_number': '1',
            'user_name': 'test',
            'password': 'test',
            'config': test_config}
        setattr(self.request, 'GET', data)
        self.assertEqual(self.rv.generate().status_int, 200)
