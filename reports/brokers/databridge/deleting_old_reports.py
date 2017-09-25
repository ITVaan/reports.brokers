# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import os
import gevent

from gevent import spawn
from datetime import datetime
from reports.brokers.databridge.base_worker import BaseWorker


class ReportCleaner(BaseWorker):
    def __init__(self, services_not_available, result_dir, cleaner_delay):
        super(ReportCleaner, self).__init__(services_not_available)
        self.start_time = datetime.now()
        self.cleaner_delay = cleaner_delay
        self.result_dir = result_dir

    def deleting_old_reports(self):
        while not self.exit:
            self.services_not_available.wait()
            for file in os.listdir(self.result_dir):
                if os.path.splitext(file)[1] == '.xlsx':
                    file_date = datetime.strptime(str(file.split('_start_date_')[0]), '%Y-%m-%d-%H-%M-%S')
                    now = datetime.now()
                    delta = now - file_date
                    if delta.days > 0:
                        os.remove(os.path.abspath(os.path.join(self.result_dir, file)))
            gevent.sleep(self.cleaner_delay)

    def _start_jobs(self):
        return {'deleting_old_reports': spawn(self.deleting_old_reports)}
