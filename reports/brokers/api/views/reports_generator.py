import os
from shutil import copyfile
from datetime import datetime
import mysql.connector as mariadb
from openpyxl import load_workbook
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
        self.cursor.execute(eval('report{}'.format(self.report_number)))
        self.templates_dir = 'templates'
        self.result_dir = 'reports'
        self.template_file_name = '{}.xlsx'.format(self.report_number)
        self.t = os.path.splitext(self.template_file_name)
        self.result_file = os.path.join(self.result_dir, datetime.now().strftime('%Y-%m-%d-%H-%M-%S') +
                                        '-report-number=' + str(self.report_number) + self.t[1])
        copyfile(os.path.join(self.templates_dir, self.template_file_name), self.result_file)
        self.wb = load_workbook(filename=self.result_file)
        self.ws = self.wb.active
        eval('self.report_{}()'.format(self.report_number))

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

    def report_2(self, start_report_period, end_report_period):
        pass

    def report_3(self, start_report_period, end_report_period):
        pass


if __name__ == '__main__':
    gor = GeneratorOfReports('22.06.2013', '22.07.2014', 1)
