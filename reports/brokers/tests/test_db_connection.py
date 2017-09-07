# -*- coding: utf-8 -*-
from datetime import datetime
from shutil import copyfile
from unittest import TestCase

import mysql.connector as mariadb
import os
import re
from openpyxl import load_workbook
from mysql.connector.constants import ClientFlag

from reports.brokers.api.selections import *
from reports.brokers.tests.utils import (copy_xls_file_from_template, create_example_worksheet,
                                                  load_and_fill_result_workbook)
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


class TestDataBaseConnection(TestCase):
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

    def test_create_empty_xls(self):
        cursor = self.conn.cursor(buffered=True)
        res = cursor.execute(report1, {'start_date': '01.05.2017', 'end_date': '01.06.2017'})
        data = [[broker_name, suppliers_count] for (broker_name, suppliers_count) in cursor]
        cursor.close()
        templates_dir = 'reports/brokers/api/views/templates'
        result_dir = 'reports/brokers/tests/test_reports'
        template_file_name = '1.xlsx'
        file_format = os.path.splitext(template_file_name)
        result_file = os.path.join(result_dir, '2017-08-05-17-00-00' + '_report-number=' +
                                   file_format[0] + file_format[1])
        copyfile(os.path.join(templates_dir, template_file_name), result_file)
        wb = load_workbook(filename=result_file)
        ws = wb.active
        row = 2
        for (broker_name, suppliers_count) in data:
            ws.cell(row=row, column=1, value=broker_name)
            ws.cell(row=row, column=2, value=suppliers_count)
            row += 1
        wb.save(result_file)

    def test_create_nonempty_xls(self):
        cursor = self.conn.cursor(buffered=True)
        start = datetime(2017, 8, 20)
        end = datetime(2017, 8, 30)
        modified = datetime(2017, 9, 2)
        cursor.execute("""
            insert into `tenders` (`original_id`,`status_id`,`broker_id`,`date_modified`,`enquiry_start_date`,
              `enquiry_end_date`) 
            values ('111', 1, 1, '{}', '{}', '{}')  
        """.format(modified, start, end))
        cursor.execute("INSERT INTO `tenderers` (`identifier`, `scheme`) VALUES ('12345', '1234');")
        cursor.execute("INSERT INTO `bids` (`original_id`, `tender_id`, `status_id`) VALUES ('111', 1, 1)")
        cursor.execute("INSERT INTO `tenderers_bids` (`tenderer_id`, `bid_id`) VALUES (1, 1)")

        res = cursor.execute(report1, {'start_date': datetime.strptime('01.05.2017', '%d.%m.%Y'),
                                       'end_date': datetime.strptime('04.09.2017', '%d.%m.%Y')})
        data = [[broker_name, suppliers_count] for (broker_name, suppliers_count) in cursor]
        cursor.close()

        result_file = copy_xls_file_from_template()
        wb = load_and_fill_result_workbook(data, result_file)
        ws = wb.active
        ws_expected = create_example_worksheet()
        self.assertEqual([row.value for col in ws for row in col], [row.value for col in ws_expected for row in col])
        wb.save(result_file)
