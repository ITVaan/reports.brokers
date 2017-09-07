# -*- coding: utf-8 -*-

from gevent import monkey

from reports.brokers.databridge.base_worker import BaseWorker
from reports.brokers.utils import get_root_pwd

monkey.patch_all()

import re
import mysql.connector as mariadb
from datetime import datetime
import gevent
import logging.config
import json
from gevent import spawn
from gevent.hub import LoopExit
from munch import munchify
from simplejson import loads
from reports.brokers.databridge.utils import journal_context

logger = logging.getLogger(__name__)


class BaseIntegration(BaseWorker):
    """ Data Bridge """

    def __init__(self, tenders_sync_client, filtered_tender_ids_queue, services_not_available, sleep_change_value,
                 db_host, db_user, db_password, database, db_charset,delay=15):
        super(BaseIntegration, self).__init__(services_not_available)
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.database = database
        self.db_charset = db_charset
        self.start_time = datetime.now()
        self.delay = delay

        # init clients
        self.tenders_sync_client = tenders_sync_client

        # init queues for workers
        self.filtered_tender_ids_queue = filtered_tender_ids_queue

        # blockers
        self.sleep_change_value = sleep_change_value

    def adding_to_db(self):
        """Get tender from filtered_tender_ids_queue put into mariaDB."""
        while not self.exit:
            self.services_not_available.wait()
            try:
                tender_id = self.filtered_tender_ids_queue.get()
            except LoopExit:
                gevent.sleep(0)
                continue
            try:
                response = self.tenders_sync_client.request("GET",
                                                            path='{}/{}'.format(self.tenders_sync_client.prefix_path,
                                                                                tender_id))
            except Exception as e:
                if getattr(e, "status_int", False) and e.status_int == 429:
                    self.sleep_change_value.increment()
                    logger.info("Waiting tender {} for sleep_change_value: {} seconds".format(
                        tender_id, self.sleep_change_value.time_between_requests))
                else:
                    logger.warning('Fail to get tender info {}'.format(tender_id),
                                   extra=journal_context(params={"TENDER_ID": tender_id}))
                    logger.exception("Message: {}".format(e.message))
                    gevent.sleep()
            else:
                self.process_items_and_move(response, tender_id)
            gevent.sleep(self.sleep_change_value.time_between_requests)


    def process_items_and_move(self, response, tender_id):
        self.sleep_change_value.decrement()
        if response.status_int == 200:
            tender_json = munchify(loads(response.body_string()))
            logger.info('Get tender {} from filtered_tender_ids_queue'.format(tender_id))

            conn = mariadb.connect(host=self.db_host, user=self.db_user, password=self.db_password,
                                   database=self.database, charset=self.db_charset)

            regex1 = re.compile(r'\\"', re.IGNORECASE)
            regex2 = re.compile(r'"\+\\u0.+?"', re.IGNORECASE)
            regex3 = re.compile(r'"\\u0.+?"', re.IGNORECASE)
            regex4 = re.compile(r'\\u0[\\u0-9a-zA-Z]*\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)
            regex5 = re.compile(r'\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)

            tender_data = tender_json['data']

            if 'enquiryPeriod' in tender_data:
                cursor = conn.cursor(buffered=False)
                str = json.dumps(tender_json, separators=(',', ':'))

                strcut = regex1.sub('', str)
                strcut = regex2.sub('""', strcut)
                strcut = regex3.sub('""', strcut)
                strcut = regex4.sub('', strcut)
                strcut = regex5.sub('', strcut)

                cursor.callproc('sp_update_tender', (strcut, tender_data['dateModified'], 0, ''))
                if "bids" in tender_data:
                    logger.info("Tender {} got. Bids count: {}".format(tender_id, len(tender_data['bids'])))

                    if len(tender_data['bids']) > 0:
                        for b in tender_data['bids']:
                            if 'tenderers' in b:
                                for tendr in b['tenderers']:
                                    pass
                else:
                    logger.info("Tender {} got without bids. Status: {}".format(tender_id, tender_data['status']))
            else:
                logger.info("Tender {} has no enquiry period! Status: {}".format(tender_id, tender_data['status']))

    def _start_jobs(self):
        return {'adding_to_db': spawn(self.adding_to_db)}
