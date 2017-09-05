import os
from shutil import copyfile
from datetime import datetime
import mysql.connector as mariadb
from mysql.connector.constants import ClientFlag
from openpyxl import load_workbook
from uuid import uuid4
from reports.brokers.api.selections import report1, report2, report3, auth, logging


class GeneratorOfReports:
    def __init__(self, start_report_period, end_report_period, report_number, user_name, password):
        # Report period
        self.start_report_period = datetime.strptime(str(start_report_period), '%d.%m.%Y')
        self.end_report_period = datetime.strptime(str(end_report_period), '%d.%m.%Y')

        # Authentication check
        self.report_number = report_number
        self.user_name = user_name
        self.password = password

        self.data = []

        # Excel directories
        self.templates_dir = 'templates'
        self.result_dir = 'reports'

        # DataBase connection
        config = {
            'user': 'root',
            'password': 'root',
            'host': 'localhost',
            'client_flags': [ClientFlag.SSL],
            'ssl_ca': '/etc/mysql/ssl/ca-cert.pem',
            'ssl_cert': '/etc/mysql/ssl/client-cert.pem',
            'ssl_key': '/etc/mysql/ssl/client-key.pem',
            'database': 'reports_data',
            'charset': 'utf8'
        }

        self.conn = mariadb.connect(**config)
        self.cursor = self.conn.cursor(buffered=True)

        # Launching of reports generator
        self.user_id = self.auth()
        if self.user_id:
            self.start_reporting()
            self.logging()
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            self.wb.save(self.result_file)
        else:
            print('Permission denied')
            exit()

    def auth(self):
        self.cursor.execute(auth, {'user_name': self.user_name, 'password': self.password})
        for i in self.cursor:
            if isinstance(i[0], int):
                return i[0]

    def start_reporting(self):
        if self.report_number == '1':
            self.cursor.execute(report1, {'start_date': self.start_report_period,
                                          'end_date': self.end_report_period})
        elif self.report_number == '2':
            self.cursor.execute(report2, {'start_date': self.start_report_period,
                                          'end_date': self.end_report_period})
        elif self.report_number == '3':
            self.cursor.execute(report3, {'start_date': self.start_report_period,
                                          'end_date': self.end_report_period})

        # Report file creation
        template_file_name = '{}.xlsx'.format(self.report_number)
        file_format = os.path.splitext(template_file_name)[1]
        self.result_file = os.path.join(self.result_dir, datetime.now().strftime('%Y-%m-%d-%H-%M-%S') +
                                        '_report-number=' + str(self.report_number) +
                                        '_' + str(self.user_id) + '_' + uuid4().hex + file_format)
        copyfile(os.path.join(self.templates_dir, template_file_name), self.result_file)
        self.wb = load_workbook(filename=self.result_file)
        self.ws = self.wb.active

        # Start
        if self.report_number == 1:
            self.report_1()
        elif self.report_number == 2:
            self.report_2()
        elif self.report_number == 3:
            self.report_3()

    def logging(self):
        self.cursor.execute(logging, {'user_id': self.user_id,
                                      'report_type_id': self.report_number,
                                      'start_report_period': self.start_report_period,
                                      'end_report_period': self.end_report_period})

    def get_path_from_hash(self, hash_file):
        for file in os.listdir(self.result_dir):
            pattern = file.split('_')[3].split('.')[0]
            if pattern == hash_file:
                return os.path.abspath(os.path.join(self.result_dir, file))
        return 'Wrong hash or this file is deleted!'

    def report_1(self):
        for broker_name, suppliers_count in self.cursor:
            self.data.append([broker_name, suppliers_count])
        row = 2
        for (broker_name, suppliers_count) in self.data:
            self.ws.cell(row=row, column=1, value=broker_name)
            self.ws.cell(row=row, column=2, value=suppliers_count)
            row += 1

    def report_2(self):
        pass

    def report_3(self):
        pass


if __name__ == '__main__':
    gor = GeneratorOfReports('01.05.2017', '01.06.2017', 1, 'test', 'test')
    print('Well done!')
