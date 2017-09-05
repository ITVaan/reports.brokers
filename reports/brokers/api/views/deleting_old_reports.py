# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

from datetime import datetime
from gevent import Greenlet
import gevent
import os

DELAY = 3600


class ReportCleaner(Greenlet):
    def __init__(self):
        super(ReportCleaner, self).__init__()
        self.start_time = datetime.now()
        self.result_dir = 'reports'

    def deleting_old_reports(self):
        for file in os.listdir(self.result_dir):
            file_date = datetime.strptime(str(file.split('_report-number=')[0]), '%Y-%m-%d-%H-%M-%S')
            now = datetime.now()
            delta = now - file_date
            if delta.days >= 1:
                os.remove(os.path.abspath(os.path.join(self.result_dir, file)))

    def launch(self):
        while True:
            self.deleting_old_reports()
            print('.')
            gevent.sleep(DELAY)


def main():
    report_cleaner = ReportCleaner()
    report_cleaner.launch()


if __name__ == "__main__":
    main()
