# coding=utf-8
from gevent import monkey

from reports.brokers.tests.utils import test_purge, execute_scripts_from_file

monkey.patch_all()

import mysql.connector as mariadb

from unittest import TestCase
from hashlib import sha256
from reports.brokers.utils import get_root_pwd


class BaseDbTestCase(TestCase):
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
        self.password = sha256("test").hexdigest()
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
        test_purge()

    def execute_example(self, f):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""DELETE FROM `tenderers_bids`""")
        cursor.execute("""DELETE FROM `bids`""")
        cursor.execute("""DELETE FROM `tenderers`""")
        cursor.execute("""DELETE FROM `tenders`""")
        cursor.close()
        return f()
