# coding=utf-8
import hashlib
from unittest import TestCase

import mysql.connector as mariadb

from reports.brokers.api.views.reports_generator import GeneratorOfReports
from reports.brokers.tests.test_db_connection import execute_scripts_from_file
from reports.brokers.tests.utils import test_config
import uuid


class TestReportsGenerator(TestCase):
    @classmethod
    def setUpClass(cls):
        config = {
            'user': 'root',
            'password': 'root',
            'host': 'localhost',
            'charset': 'utf8'
        }
        cls.conn = mariadb.connect(**config)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.password = hashlib.sha256("test").hexdigest()
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
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("test", "{}", 0);""".format(
            self.password))
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2017', '01.06.2017', '1', 'test', 'test', test_config)
        self.assertEqual(rep_gen.report_number, '1')
        self.assertEqual(rep_gen.password, self.password)
        self.assertEqual(rep_gen.config, test_config)

    def test_permission(self):
        rep_gen = GeneratorOfReports('01.05.2017', '01.06.2017', '1', 'test', 'test', test_config)
        self.assertEqual(rep_gen.report_number, '1')
        self.assertNotEqual(rep_gen.password, 'test')
        self.assertEqual(rep_gen.config, test_config)

    def test_start_reporting(self):
        date = '2017-05-02 13:00:00.000000'
        tender_id = uuid.uuid4().hex
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("test", "{}", 0);""".format(self.password))
        cursor.execute("""INSERT INTO `brokers` (code) VALUES ("test");""")
        cursor.execute("""INSERT INTO `tenders` (`original_id`, `status_id`, `broker_id`, `date_modified`, 
                                              `enquiry_start_date`, `enquiry_end_date`) 
                       VALUES ('{}', '5', 1, "{}", "{}", "{}");""".format(tender_id, date, date, date))
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2016', '01.06.2018', '1', 'test', 'test', test_config)
        self.assertEqual(rep_gen.report_number, '1')
        self.assertEqual(rep_gen.password, self.password)
        self.assertEqual(rep_gen.config, test_config)
