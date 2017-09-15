# -*- coding: utf-8 -*-

from gevent import monkey

from reports.brokers.databridge.base_worker import BaseWorker

monkey.patch_all()
from yaml import load
from datetime import datetime
import gevent
from gevent import spawn
import os

DELAY = 3


class ReportCleaner(BaseWorker):
    def __init__(self, services_not_available):
        super(ReportCleaner, self).__init__(services_not_available)
        self.start_time = datetime.now()
        self.result_dir = self.config_get("result_dir")

    def deleting_old_reports(self):
        while not self.exit:
            self.services_not_available.wait()
            for file in os.listdir(self.result_dir):
                if os.path.splitext(file)[1] == '.xlsx':
                    file_date = datetime.strptime(str(file.split('_report_number_')[0]), '%Y-%m-%d-%H-%M-%S')
                    now = datetime.now()
                    delta = now - file_date
                    if delta.days >= 0:
                        os.remove(os.path.abspath(os.path.join(self.result_dir, file)))
            gevent.sleep(DELAY)

    def config_get(self, name):
        with open("etc/reports_brokers.yaml") as config_file_obj:
            config = load(config_file_obj.read())
        return config.get(name)

    def _start_jobs(self):
        return {'deleting_old_reports': spawn(self.deleting_old_reports)}
