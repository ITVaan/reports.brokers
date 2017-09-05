# coding=utf-8
from unittest import TestCase

import mysql.connector as mariadb

from reports.brokers.api.views.reports_generator import GeneratorOfReports
from reports.brokers.tests.test_db_connection import execute_scripts_from_file
from reports.brokers.utils import get_root_pwd
from mock import MagicMock


class TestReportsGenerator(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = mariadb.connect(host='127.0.0.1', user='root', password=get_root_pwd())

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""DROP DATABASE IF EXISTS reports_data_test;""")
        cursor.execute("""CREATE DATABASE IF NOT EXISTS reports_data_test;""")
        cursor.execute("""USE reports_data_test""")
        execute_scripts_from_file(cursor, "reports/brokers/database/reports_data_dev.sql")
        cursor.close()

    def tearDown(self):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""DROP DATABASE IF EXISTS reports_data_test;""")
        cursor.close()

    def test_init(self):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""insert into `users` (`user_name`, `password`, `blocked`) values ("Vlad", "1234", 0);""")
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2017', '01.06.2017', 1, 'Vlad', '1234', "reports_data_test")
        self.assertEqual(rep_gen.report_number, 1)
