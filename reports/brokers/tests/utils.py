# -*- coding: utf-8 -*-
from openpyxl import Workbook, load_workbook
from os import path
from shutil import copyfile
from gevent import sleep as gsleep

from reports.brokers.utils import get_root_pwd

test_config = {
    'main': {
        'db_user': 'root',
        'db_password': get_root_pwd(),
        'db_host': 'localhost',
        'database': 'reports_data_test',
        'db_charset': 'utf8',
        'templates_dir': "reports/brokers/api/views/templates",
        'result_dir': path.join(path.dirname(path.realpath(__file__)), "test_reports")
    }
}


def copy_xls_file_from_template():
    template_file_name = '1.xlsx'
    t = path.splitext(template_file_name)
    result_file = path.join(test_config['main']['result_dir'], t[0] + '-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + t[1])
    copyfile(path.join(test_config['main']['templates_dir'], template_file_name), result_file)

    return result_file


def create_example_worksheet():
    wb_expected = Workbook()
    ws_expected = wb_expected.active
    ws_expected.title = u"Лист1"
    ws_expected.cell(row=1, column=1, value="Площадка")
    ws_expected.cell(row=1, column=2, value="Кількість нових учасників")
    ws_expected.cell(row=2, column=1, value="prom.ua")
    ws_expected.cell(row=2, column=2, value=1)
    return ws_expected


def load_and_fill_result_workbook(data, result_file):
    res = load_workbook(filename=result_file)
    ws = res.active
    row = 2
    for (broker_name, suppliers_count) in data:
        ws.cell(row=row, column=1, value=broker_name)
        ws.cell(row=row, column=2, value=suppliers_count)
        row += 1
    return res


def custom_sleep(seconds=0):
    return gsleep(seconds=0)
