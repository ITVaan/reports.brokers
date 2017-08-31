import os
from shutil import copyfile
from datetime import datetime, timedelta
import mysql.connector as mariadb
from openpyxl import load_workbook
import hashlib
from reports.brokers.api.selections import report1, report2, report3


class GeneratorOfReports:
    def __init__(self, start_report_period, end_report_period, report_number):
        self.start_report_period = datetime.strptime(str(start_report_period), '%d.%m.%Y')
        self.end_report_period = datetime.strptime(str(end_report_period), '%d.%m.%Y')
        self.report_number = report_number
        self.data = []
        self.conn = mariadb.connect(host='127.0.0.1', user='root', password='root', database='reports_data',
                                    charset='utf8')
        self.cursor = self.conn.cursor(buffered=True)
        self.cursor.execute(eval('report{}'.format(self.report_number)), {'start_date': self.start_report_period,
                                                                          'end_date': self.end_report_period})
        self.templates_dir = 'templates'
        self.result_dir = 'reports'

        self.deleting_old_reports()

        self.template_file_name = '{}.xlsx'.format(self.report_number)
        self.t = os.path.splitext(self.template_file_name)
        self.result_file = os.path.join(self.result_dir, datetime.now().strftime('%Y-%m-%d-%H-%M-%S') +
                                        '-report-number=' + str(self.report_number) + self.t[1])
        copyfile(os.path.join(self.templates_dir, self.template_file_name), self.result_file)
        self.wb = load_workbook(filename=self.result_file)
        self.ws = self.wb.active
        eval('self.report_{}()'.format(self.report_number))

    def deleting_old_reports(self):
        for file in os.listdir(self.result_dir):
            file_date = datetime.strptime(str(file.split('-report-number=')[0]), '%Y-%m-%d-%H-%M-%S')
            now = datetime.now()
            delta = now - file_date
            if delta.days >= 1:
                os.remove(os.path.abspath(os.path.join(self.result_dir, file)))

    def get_hash_from_filename(self):
        file_name = os.path.split(self.result_file)[1]
        hasher = hashlib.md5(file_name)
        return hasher.hexdigest()

    def get_path_from_hash(self, hash_file):
        for file in os.listdir(self.result_dir):
            hasher = hashlib.md5(file)
            if hasher.hexdigest() == hash_file:
                return os.path.abspath(os.path.join(self.result_dir, file))
        return 'Wrong hash or this file is deleted!'

    def report_1(self):

        for broker_name, suppliers_count in self.cursor:
            self.data.append([broker_name, suppliers_count])

        self.cursor.close()
        self.conn.close()
        row = 2
        for (broker_name, suppliers_count) in self.data:
            self.ws.cell(row=row, column=1, value=broker_name)
            self.ws.cell(row=row, column=2, value=suppliers_count)
            row += 1
        self.wb.save(self.result_file)
        return self.get_hash_from_filename()

    def report_2(self):
        pass

    def report_3(self):
        pass


if __name__ == '__main__':
    gor = GeneratorOfReports('01.05.2017', '01.06.2017', 1)
