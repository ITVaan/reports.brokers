# coding=utf-8
import hashlib

from reports.brokers.api.views.reports_generator import GeneratorOfReports
from reports.brokers.tests.base_db_test import BaseDbTestCase
from reports.brokers.tests.utils import test_config


class TestReportsGenerator(BaseDbTestCase):

    def test_init(self):
        cursor = self.conn.cursor(buffered=True)
        password = hashlib.sha256("1234").hexdigest()
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("Vlad", "{}", 0);""".format(
            password))
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2017', '01.06.2017', 1, 'Vlad', '1234', test_config)
        self.assertEqual(rep_gen.report_number, 1)
        self.assertEqual(rep_gen.password, password)
        self.assertEqual(rep_gen.config, test_config)
