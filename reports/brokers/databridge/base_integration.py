# -*- coding: utf-8 -*-
import os
import re
import mysql.connector as mariadb
import gevent
import logging.config
import json
from gevent.event import Event
from gevent import Greenlet, spawn
from munch import munchify
from restkit import ResourceError
from simplejson import loads

logger = logging.getLogger(__name__)


class BaseIntegration(Greenlet):
    """ Edr API Data Bridge """

    def __init__(self, tenders_sync_client, filtered_tender_ids_queue, services_not_available, sleep_change_value,
                 delay=15):
        super(BaseIntegration, self).__init__()
        self.exit = False
        self.delay = delay

        # init clients
        self.tenders_sync_client = tenders_sync_client

        # init queues for workers
        self.filtered_tender_ids_queue = filtered_tender_ids_queue

        # blockers
        self.initialization_event = Event()
        self.sleep_change_value = sleep_change_value
        self.services_not_available = services_not_available

    def adding_to_db(self):
        while True:
            try:
                tender_id = self.filtered_tender_ids_queue.get()
                response = self.tenders_sync_client.request("GET",
                                                            path='{}/{}'.format(self.tenders_sync_client.prefix_path,
                                                                                tender_id))
            except ResourceError as res:
                if res.status_int == 429:
                    self.sleep_change_value.increment()
                    logger.info("Waiting tender {} for sleep_change_value: {} seconds".format(tender_id,
                                                                                              self.sleep_change_value.time_between_requests))
                else:
                    logger.warning('Fail to get tender info {}'.format(tender_id))
                    logger.exception("Message: {}, status_code {}".format(res.msg, res.status_int))
                    logger.info('Leave tender {} in tenders queue'.format(tender_id))
                    gevent.sleep()
            except Exception as e:
                logger.warning('Fail to get tender info {}'.format(tender_id))
                logger.exception("Message: {}".format(e.message))
                logger.info('Leave tender {} in tenders queue'.format(tender_id))
                gevent.sleep()
            else:
                self.sleep_change_value.decrement()
                if response.status_int == 200:
                    tender_json = munchify(loads(response.body_string()))
                logger.info('Get tender {} from filtered_tender_ids_queue'.format(tender_id))

                conn = mariadb.connect(host='localhost', user='root', password='root', database='reports_data',
                                       charset='utf8')

                regex1 = re.compile(r'\\"', re.IGNORECASE)
                regex2 = re.compile(r'"\+\\u0.+?"', re.IGNORECASE)
                regex3 = re.compile(r'"\\u0.+?"', re.IGNORECASE)
                regex4 = re.compile(r'\\u0[\\u0-9a-zA-Z]*\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)
                regex5 = re.compile(r'\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)

                tender_data = tender_json['data']
                id = tender_data['id']

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
                        logger.info("Tender {0} got. Bids count: {1}".format(id, len(tender_data['bids'])))

                        if len(tender_data['bids']) > 0:
                            for b in tender_data['bids']:
                                if 'tenderers' in b:
                                    for tendr in b['tenderers']:
                                        pass
                    else:
                        logger.info("Tender {0} got without bids. Status: {1}".format(id, tender_data['status']))
                else:
                    logger.info("Tender {0} has no enquiry period! Status: {1}".format(id, tender_data['status']))

    def _start_synchronization_workers(self):
        logger.info('BaseIntegration starting sync workers')
        self.jobs = spawn(self.adding_to_db())

    def _restart_synchronization_workers(self):
        logger.warning('Restarting synchronization')
        for j in self.jobs:
            j.kill(timeout=5)
        self._start_synchronization_workers()

    def _run(self):
        logger.info('Start BaseIntegration')
        self.services_not_available.wait()
        self._start_synchronization_workers()
        worker = self.jobs
        try:
            while not self.exit:
                self.services_not_available.wait()
                gevent.sleep(self.delay)
                if worker.dead:
                    self._restart_synchronization_workers()
                    worker = self.jobs
        except Exception as e:
            logger.exception(e)
            raise e

    def shutdown(self):
        self.exit = True
        logger.info('Worker BaseIntegration complete his job.')
