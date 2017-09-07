# coding=utf-8
import hashlib
from unittest import TestCase
from os import path

import mysql.connector as mariadb
from mysql.connector.constants import ClientFlag

from reports.brokers.api.views.reports_generator import GeneratorOfReports
from reports.brokers.tests.test_db_connection import execute_scripts_from_file
from reports.brokers.tests.utils import test_config
from reports.brokers.utils import get_root_pwd


class TestReportsGenerator(TestCase):
    @classmethod
    def setUpClass(cls):
        config = {
            'user': 'root',
            'password': get_root_pwd(),
            'host': 'localhost',
            'charset': 'utf8'
        }
        cls.conn = mariadb.connect(**config)

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
        password = hashlib.sha256("1234").hexdigest()
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("Vlad", "{}", 0);""".format(
            password))
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2017', '01.06.2017', 1, 'Vlad', '1234', test_config)
        self.assertEqual(rep_gen.report_number, 1)
        self.assertEqual(rep_gen.password, password)
        self.assertEqual(rep_gen.config, test_config)
