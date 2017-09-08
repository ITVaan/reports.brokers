# coding=utf-8
import hashlib
from datetime import datetime
from shutil import copyfile
from uuid import uuid4

import mysql.connector as mariadb
import os
from openpyxl import load_workbook
from yaml import load

from reports.brokers.api.selections import *
from reports.brokers.utils import get_root_pwd

from logging import getLogger
LOGGER = getLogger("{}.init".format(__name__))


class GeneratorOfReports(object):
    def __init__(self, start_report_period, end_report_period, report_number, user_name, password, config):
        # Report period
        self.start_report_period = datetime.strptime(str(start_report_period), '%d.%m.%Y')
        self.end_report_period = datetime.strptime(str(end_report_period), '%d.%m.%Y')

        # Authentication check
        self.report_number = report_number
        self.user_name = user_name
        self.password = hashlib.sha256(password).hexdigest()
        self.config = config

        self.data = []

        # Excel directories
        self.templates_dir = self.config_get("templates_dir")
        self.result_dir = self.config_get("result_dir")

        # DataBase connection
        self.conn = mariadb.connect(host=self.config_get("db_host"), user=self.config_get("db_user"),
                                    password=get_root_pwd(), database=self.config_get("database"),
                                    charset=self.config_get("db_charset") or 'utf8')
        self.cursor = self.conn.cursor(buffered=True)

        # Launching of reports generator
        self.user_id = self.auth()
        if self.user_id:
            self.date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            self.uuid = uuid4().hex
            self.start_reporting()
            self.logging()
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            self.wb.save(self.result_file)
        else:
            print('Permission denied')
            exit()

    def config_get(self, name):
        return self.config.get(name)
        # return self.config.get('main').get(name)

    def auth(self):
        self.cursor.execute(auth, {'user_name': self.user_name, 'password': self.password})
        for i in self.cursor:
            if isinstance(i[0], int):
                return i[0]

    def start_reporting(self):
        # Report file creation
        LOGGER.info("Start reporting")

        template_file_name = '{}.xlsx'.format(self.report_number)
        file_format = os.path.splitext(template_file_name)[1]
        self.result_file = os.path.join(self.result_dir, self.filename(file_format))
        copyfile(os.path.join(self.templates_dir, template_file_name), self.result_file)
        self.wb = load_workbook(filename=self.result_file)
        self.ws = self.wb.active

        # Start
        LOGGER.info("Start reporting 2: rep_number={}; type {}".format(self.report_number, type(self.report_number)))
        if self.report_number == '1':
            self.cursor.execute(report1, {'start_date': self.start_report_period, 'end_date': self.end_report_period})
            self.report_1()
        elif self.report_number == '2':
            self.cursor.execute(report2, {'start_date': self.start_report_period, 'end_date': self.end_report_period})
            self.report_2()
        elif self.report_number == '3':
            self.cursor.execute(report3, {'start_date': self.start_report_period, 'end_date': self.end_report_period})
            self.report_3()

    def logging(self):
        self.cursor.execute(logging, {'user_id': self.user_id,
                                      'report_type_id': self.report_number,
                                      'start_report_period': self.start_report_period,
                                      'end_report_period': self.end_report_period})

    def filename(self, file_format):
        return "{date}_report_number_{num}_{uid}_{uuid4}{ext}".format(date=self.date,
                                                                      num=str(self.report_number),
                                                                      uid=str(self.user_id),
                                                                      uuid4=self.uuid, ext=file_format)

    def get_path_from_hash(self, hash_file):
        for file in os.listdir(self.result_dir):
            pattern = file.split('_')[3].split('.')[0]
            if pattern == hash_file:
                return os.path.abspath(os.path.join(self.result_dir, file))
        return 'Wrong hash or this file is deleted!'

    def report_1(self):
        LOGGER.info("report 1")
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
    with open("/home/dtrenkenshu/PycharmProjects/reports.brokers/etc/reports_brokers.yaml") as config_file_obj:
        config = load(config_file_obj.read())
    os.chdir("/home/dtrenkenshu/PycharmProjects/reports.brokers")
    gor = GeneratorOfReports('01.05.2017', '01.06.2017', 1, 'test', 'test', config)
    print('Well done!')
