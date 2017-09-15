# coding=utf-8
import hashlib
import re
from gevent import monkey
monkey.patch_all()
import mysql.connector as mariadb

from unittest import TestCase

from reports.brokers.utils import get_root_pwd


def execute_scripts_from_file(cursor, filename):
    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sql_file = fd.read()
    fd.close()
    # Find special delimiters
    delimiters = re.compile('DELIMITER *(\S*)', re.I)
    result = delimiters.split(sql_file)
    # Insert default delimiter and separate delimiters and sql
    result.insert(0, ';')
    delimiter = result[0::2]
    section = result[1::2]
    for i in range(len(delimiter)):
        queries = section[i].split(delimiter[i])
        for query in queries:
            if not query.strip():
                continue
            cursor.execute(query)


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
