# -*- coding: utf-8 -*-

from gevent import monkey

from reports.brokers.databridge.base_worker import BaseWorker

monkey.patch_all()

import mysql.connector as mariadb
from datetime import datetime
import gevent
import logging.config
import json
from gevent import spawn
from gevent.hub import LoopExit
from munch import munchify
from simplejson import loads
from reports.brokers.databridge.utils import journal_context, EdrDocument
from restkit.errors import ResourceError

logger = logging.getLogger(__name__)


class BaseIntegration(BaseWorker):
    """ Data Bridge """

    def __init__(self, tenders_sync_client, filtered_tender_ids_queue, processing_docs_queue, services_not_available, sleep_change_value,
                 db_host, db_user, db_password, database, db_charset, delay=15):
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
        self.processing_docs_queue = processing_docs_queue

        # blockers
        self.sleep_change_value = sleep_change_value

    def adding_to_db(self):
        """Get tender from filtered_tender_ids_queue put into mariaDB."""
        while not self.exit:
            self.services_not_available.wait()
            try:
                tender_id = self.filtered_tender_ids_queue.get()
            except LoopExit:
                gevent.sleep()
                continue
            try:
                response = self.tenders_sync_client.request("GET",
                                                            path='{}/{}'.format(self.tenders_sync_client.prefix_path,
                                                                                tender_id))
            except ResourceError as reserr:
                if reserr.status_int == 429:
                    self.sleep_change_value.increment()
                    logger.info("Waiting tender {} for sleep_change_value: {} seconds".format(
                        tender_id, self.sleep_change_value.time_between_requests))
                else:
                    logger.warning('Fail to get tender info {}'.format(tender_id),
                                   extra=journal_context(params={"TENDER_ID": tender_id}))
                    logger.exception("Message: {}".format(reserr.message))
                    gevent.sleep()
            except Exception as e:
                logger.warning('Fail to get tender info {}'.format(tender_id),
                               extra=journal_context(params={"TENDER_ID": tender_id}))
                logger.exception("Message: {}".format(e.message))
                logger.info('Leave tender {} in tenders queue'.format(tender_id),
                            extra=journal_context(params={"TENDER_ID": tender_id}))
                gevent.sleep()
            else:
                self.process_items_and_move(response, tender_id)
            gevent.sleep(self.sleep_change_value.time_between_requests)

    def processing_docs(self, tender_data):
        tender_id = tender_data['id']
        if 'awards' in tender_data:
            for aw in tender_data['awards']:
                if 'documents' in aw:
                    for doc in aw['documents']:
                        doc_url = doc['url']
                        if 'bid_id' in aw:
                            bid_id = aw['bid_id']
                            self.processing_docs_queue.put(EdrDocument(tender_id, bid_id, doc_url))
                            logger.info('Processing_docs data: {}'.format(EdrDocument(tender_id, bid_id, doc_url)))
                        else:
                            logger.info('Tender {} award {} has no bidID'.format(tender_id, aw['id']))
                else:
                    logger.info('Tender {} award {} has no documents'.format(tender_id, aw['id']))
        else:
            logger.info('Tender {} has no awards'.format(tender_id))

    def process_items_and_move(self, response, tender_id):
        self.sleep_change_value.decrement()
        if response.status_int == 200:
            tender_json = munchify(loads(response.body_string().decode("utf-8")))
            tender_data = tender_json['data']
            self.processing_docs(tender_data)
            json_to_str = json.dumps(tender_data)
            logger.info('Get tender {} from filtered_tender_ids_queue'.format(tender_id))
            conn = mariadb.connect(host=self.db_host, user=self.db_user, password=self.db_password,
                                   database=self.database, charset=self.db_charset)
            cursor = conn.cursor(buffered=False)
            cursor.callproc('sp_update_tender', (json_to_str, tender_data['dateModified'], 0, ''))
            if "bids" in tender_data:
                logger.info("Tender {} got. Bids count: {}".format(tender_id, len(tender_data['bids'])))
            else:
                logger.info("Tender {} got without bids. Status: {}".format(tender_id, tender_data['status']))

    def _start_jobs(self):
        return {'adding_to_db': spawn(self.adding_to_db)}
