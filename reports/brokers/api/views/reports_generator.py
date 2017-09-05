# coding=utf-8
import os
from shutil import copyfile
from datetime import datetime
import mysql.connector as mariadb
from openpyxl import load_workbook
from uuid import uuid4
from reports.brokers.api.selections import report1, report2, report3, auth
from reports.brokers.utils import get_root_pwd


class GeneratorOfReports:
    def __init__(self, start_report_period, end_report_period, report_number, user_name, password, db_name):
        # Report period
        self.start_report_period = datetime.strptime(str(start_report_period), '%d.%m.%Y')
        self.end_report_period = datetime.strptime(str(end_report_period), '%d.%m.%Y')

        # Authentication check
        self.report_number = report_number
        self.user_name = user_name
        self.password = password

        self.data = []

        # Excel directories
        self.templates_dir = 'reports/brokers/api/views/templates'
        self.result_dir = 'reports/reports'

        self.deleting_old_reports()

        # DataBase connection
        self.conn = mariadb.connect(host='127.0.0.1', user='root', password=get_root_pwd(), database=db_name, charset='utf8')
        self.cursor = self.conn.cursor(buffered=True)

        if self.auth():
            self.start_reporting()
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
                self.user_id = i[0]
                return True
            else:
                return False

    def start_reporting(self):
        self.cursor.execute(eval('report{}'.format(self.report_number)), {'start_date': self.start_report_period,
                                                                          'end_date': self.end_report_period})
        # Report file creation
        template_file_name = '{}.xlsx'.format(self.report_number)
        t = os.path.splitext(template_file_name)
        self.result_file = os.path.join(self.result_dir, self.filename(t))
        copyfile(os.path.join(self.templates_dir, template_file_name), self.result_file)
        self.wb = load_workbook(filename=self.result_file)
        self.ws = self.wb.active
        # Start
        eval('self.report_{}()'.format(self.report_number))

    def filename(self, t):
        return "{date}_report-number={num}_{uid}_{uuid4}{ext}".format(date=datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                                                                      num=str(self.report_number),
                                                                      uid=str(self.user_id),
                                                                      uuid4=uuid4().hex, ext=t[1])

    def deleting_old_reports(self):
        for file in os.listdir(self.result_dir):
            file_date = datetime.strptime(str(file.split('_report-number=')[0]), '%Y-%m-%d-%H-%M-%S')
            now = datetime.now()
            delta = now - file_date
            if delta.days >= 1:
                os.remove(os.path.abspath(os.path.join(self.result_dir, file)))

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
    gor = GeneratorOfReports('01.05.2017', '01.06.2017', 1, 'Vlad', '1234')
    print('Well done!')
