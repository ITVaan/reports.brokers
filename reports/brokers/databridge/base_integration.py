# -*- coding: utf-8 -*-
import os
import re
import mysql.connector as mariadb
import gevent
import logging.config
import json
import dateutil.parser
from gevent.event import Event
from gevent import Greenlet, spawn
from munch import munchify
from restkit import ResourceError
from simplejson import loads

logger = logging.getLogger(__name__)


class BaseIntegration(Greenlet):
    """ Edr API Data Bridge """

    def __init__(self, tenders_sync_client, filtered_tender_ids_queue, services_not_available, sleep_change_value,
                 delay=2):
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
        tenders_subdir = 'tenders'
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
                    tender_json = munchify(loads(response.body_string()))['data']
                logger.info('Get tender {} from filtered_tender_ids_queue'.format(tender_id))
            if not os.path.exists(tenders_subdir):
                os.makedirs(tenders_subdir)

            conn = mariadb.connect(host='127.0.0.1', user='root', password='root', database='reports_data',
                                   charset='utf8')

            regex1 = re.compile(r'\\"', re.IGNORECASE)
            regex2 = re.compile(r'"\+\\u0.+?"', re.IGNORECASE)
            regex3 = re.compile(r'"\\u0.+?"', re.IGNORECASE)
            regex4 = re.compile(r'\\u0[\\u0-9a-zA-Z]*\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)
            regex5 = re.compile(r'\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)

            t = tender_json
            logger.info('vot nash tender = {}'.format(t))
            dtm = dateutil.parser.parse(t['dateModified'])
            id = t['id']
            subdir = '{0}/{1:04d}-{2:02d}-{3:02d}'.format(tenders_subdir, dtm.year, dtm.month, dtm.day)
            if not os.path.exists(subdir):
                os.makedirs(subdir)

            file_path = "{0}/{1}.json".format(subdir, id)
            pretty_file_path = "{0}/{1}_pretty.json".format(subdir, id)

            if not os.path.exists(file_path) or not os.path.exists(pretty_file_path):
                if response.status_code == 200:
                    response_json = response.json()

                    with open(file_path, "w") as text_file:
                        json.dump(response_json, text_file, separators=(',', ':'))

                    with open(pretty_file_path, "w") as text_file:
                        json.dump(response_json, text_file, sort_keys=True, indent=2, separators=(',', ': '))
                else:
                    print('Failed to get tender {0}! Error: {1} {2}'.format(id, response.status_code, response.text))
            else:
                print('Tender {0} already got.'.format(id))

                with open(file_path, "r") as text_file:
                    response_json = json.load(text_file)

            tender_data = response_json['data']

            if 'enquiryPeriod' in tender_data:

                cursor = conn.cursor(buffered=False)
                str = json.dumps(response_json, separators=(',', ':'))

                strcut = regex1.sub('', str)
                strcut = regex2.sub('""', strcut)
                strcut = regex3.sub('""', strcut)
                strcut = regex4.sub('', strcut)
                strcut = regex5.sub('', strcut)

                res = cursor.callproc('sp_update_tender',
                                      (strcut, t['dateModified'], 0, ''))
                if res[2] != 0:
                    print(str)
                    print(strcut)
                    print('!!!!  sp_update_tender result for {0}: {1}; {2}'.format(id, res[2], res[3]))

                if "bids" in tender_data:
                    # print("Tender {0} got. Bids count: {1}".format(id, len(tender_data['bids'])))

                    if len(tender_data['bids']) > 0:
                        for b in tender_data['bids']:
                            if 'tenderers' in b:
                                for tendr in b['tenderers']:
                                    # print(u'Got tenderer: {0} {1} {2}'.format(tendr['identifier']['id'], tendr['identifier']['scheme'], tendr['identifier']['legalName']))
                                    # .decode("utf-8")
                                    pass
                else:
                    print("Tender {0} got without bids. Status: {1}".format(id, tender_data['status']))

            else:
                print("Tender {0} has no enquiry period! Status: {1}".format(id, tender_data['status']))

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
