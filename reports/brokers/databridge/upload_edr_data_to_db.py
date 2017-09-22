# coding=utf-8
from gevent import monkey
monkey.patch_all()
import mysql.connector as mariadb

from reports.brokers.databridge.base_worker import BaseWorker
from gevent import sleep as gsleep, spawn
from datetime import datetime


class UploadEdrDataToDbWorker(BaseWorker):

    def __init__(self, services_not_available, edr_data_to_database,
                 sleep_change_value, db_host, db_user, db_password, database, db_charset, delay=15):
        super(UploadEdrDataToDbWorker, self).__init__(services_not_available)
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.database = database
        self.db_charset = db_charset
        self.start_time = datetime.now()
        self.delay = delay
        self.edr_data_to_database = edr_data_to_database
        self.sleep_change_value = sleep_change_value

    def adding_edr_data_to_db(self):
        while not self.exit:
            data = self.edr_data_to_database.get()
            self.load_into_db(data)
            gsleep()

    def load_into_db(self, edr_data):
        conn = mariadb.connect(host=self.db_host, user=self.db_user, password=self.db_password,
                               database=self.database, charset=self.db_charset)
        cursor = conn.cursor(buffered=False)
        # cursor.execute("sp_update_tenderer", (edr_data.identifier, edr_data.scheme,
        #                                       edr_data.edr_date, edr_data.edr_status))

    def _start_jobs(self):
        return {'adding_to_db': spawn(self.adding_edr_data_to_db)}

