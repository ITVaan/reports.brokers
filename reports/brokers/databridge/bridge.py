# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser

from gevent import monkey
from reports.brokers.databridge.doc_service_client import DocServiceClient
from reports.brokers.databridge.download_from_doc_service import DownloadFromDocServiceWorker

monkey.patch_all()

import logging
import logging.config
import os
import argparse
import gevent

from functools import partial
from gevent import event
from gevent.queue import Queue
from retrying import retry
from restkit import RequestError, ResourceError
from constants import retry_mult

from openprocurement_client.client import TendersClientSync as BaseTendersClientSync, TendersClient as BaseTendersClient
from reports.brokers.databridge.scanner import Scanner
from reports.brokers.databridge.base_integration import BaseIntegration
from reports.brokers.databridge.deleting_old_reports import ReportCleaner
from reports.brokers.databridge.utils import journal_context, check_412
from reports.brokers.utils import get_root_pwd
from reports.brokers.databridge.journal_msg_ids import (DATABRIDGE_RESTART_WORKER, DATABRIDGE_START,
                                                        DATABRIDGE_DOC_SERVICE_CONN_ERROR)

from reports.brokers.databridge.sleep_change_value import APIRateController

logger = logging.getLogger(__name__)


class TendersClientSync(BaseTendersClientSync):
    @check_412
    def request(self, *args, **kwargs):
        return super(TendersClientSync, self).request(*args, **kwargs)


class TendersClient(BaseTendersClient):
    @check_412
    def _create_tender_resource_item(self, *args, **kwargs):
        return super(TendersClient, self)._create_tender_resource_item(*args, **kwargs)


class DataBridge(object):
    """ Data Bridge """

    def __init__(self, config):
        super(DataBridge, self).__init__()
        self.config = config
        api_server = self.config_get('tenders_api_server')
        self.api_version = self.config_get('tenders_api_version')
        ro_api_server = self.config_get('public_tenders_api_server') or api_server
        buffers_size = int(self.config_get('buffers_size')) or 500
        self.delay = int(self.config_get('delay')) or 15
        self.cleaner_delay = int(self.config_get('cleaner_delay')) or 15
        self.increment_step = int(self.config_get('increment_step')) or 1
        self.decrement_step = int(self.config_get('decrement_step')) or 1
        self.sleep_change_value = APIRateController(self.increment_step, self.decrement_step)
        self.database = self.config_get('database') or None
        self.result_dir = self.config_get("result_dir") or "reports_finished_reports"

        # init clients
        self.tenders_sync_client = TendersClientSync('', host_url=ro_api_server, api_version=self.api_version)
        self.client = TendersClient(self.config_get('api_token'), host_url=api_server, api_version=self.api_version)
        self.doc_client = DocServiceClient("https://public.api-sandbox.openprocurement.org")

        # init queues for workers
        self.filtered_tender_ids_queue = Queue(maxsize=buffers_size)  # queue of tender IDs with appropriate status
        self.processing_docs_queue = Queue(maxsize=buffers_size)  # queue of tender IDs, bid IDs and doc. urls
        self.edr_data_to_database_queue = Queue(maxsize=buffers_size)

        # blockers
        self.initialization_event = event.Event()
        self.services_not_available = event.Event()

        # Workers
        self.scanner = partial(Scanner.spawn,
                               tenders_sync_client=self.tenders_sync_client,
                               filtered_tender_ids_queue=self.filtered_tender_ids_queue,
                               services_not_available=self.services_not_available,
                               sleep_change_value=self.sleep_change_value,
                               delay=self.delay)
        self.base_integration = partial(BaseIntegration.spawn,
                                        tenders_sync_client=self.tenders_sync_client,
                                        filtered_tender_ids_queue=self.filtered_tender_ids_queue,
                                        processing_docs_queue=self.processing_docs_queue,
                                        services_not_available=self.services_not_available,
                                        sleep_change_value=self.sleep_change_value,
                                        db_host=self.config_get("db_host"),
                                        db_user=self.config_get("db_user"),
                                        db_password=get_root_pwd(),
                                        database=self.config_get("database"),
                                        db_charset=self.config_get("db_charset"),
                                        delay=self.delay)

        self.report_cleaner = partial(ReportCleaner.spawn,
                                      services_not_available=self.services_not_available,
                                      result_dir=self.result_dir,
                                      cleaner_delay=self.cleaner_delay)

        self.download_from_doc_service = partial(DownloadFromDocServiceWorker.spawn,
                                                 services_not_available=self.services_not_available,
                                                 doc_client=self.doc_client,
                                                 items_to_download_queue=self.processing_docs_queue,
                                                 edr_data_to_database=self.edr_data_to_database_queue)

    def config_get(self, name):
        return self.config.get('app:api', name)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=retry_mult)
    def check_openprocurement_api(self):
        """Makes request to the TendersClient, returns True if it's up, raises RequestError otherwise"""
        try:
            self.client.head('/api/{}/spore'.format(self.api_version))
        except (RequestError, ResourceError) as e:
            logger.info('TendersServer connection error, message {}'.format(e),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_DOC_SERVICE_CONN_ERROR}, {}))
            raise e
        else:
            return True

    def set_sleep(self):
        self.services_not_available.clear()

    def set_wake_up(self):
        self.services_not_available.set()

    def all_available(self):
        try:
            self.check_openprocurement_api()
        except Exception as e:
            logger.info("Service is unavailable, message {}".format(e))
            return False
        else:
            return True

    def check_services(self):
        if self.all_available():
            logger.info("All services are available")
            self.set_wake_up()
        else:
            logger.info("Pausing")
            self.set_sleep()

    def _start_jobs(self):
        self.jobs = {'Scanner': self.scanner(),
                     'BaseIntegration': self.base_integration(),
                     'ReportCleaner': self.report_cleaner(),
                     'DownloadFromDocServiceWorker': self.download_from_doc_service()}

    def launch(self):
        while True:
            if self.all_available():
                self.run()
                break
            gevent.sleep(self.delay)

    def run(self):
        logger.info('Start Data Bridge', extra=journal_context({"MESSAGE_ID": DATABRIDGE_START}, {}))
        self._start_jobs()
        counter = 0
        try:
            while True:
                gevent.sleep(self.delay)
                self.check_services()
                if counter == 5:
                    counter = 0
                    logger.info('Current state: Filtered tenders {}'.format(self.filtered_tender_ids_queue.qsize()))
                    logger.info('Current state: Processing docs {}'.format(self.processing_docs_queue.qsize()))
                counter += 1
                self.check_and_revive_jobs()
        except KeyboardInterrupt:
            logger.info('Exiting...')
            gevent.killall(self.jobs, timeout=5)
        except Exception as e:
            logger.error(e)

    def check_and_revive_jobs(self):
        for name, job in self.jobs.items():
            logger.debug("{}.dead: {}".format(name, job.dead))
            if job.dead:
                self.revive_job(name)

    def revive_job(self, name):
        logger.warning('Restarting {} worker'.format(name),
                       extra=journal_context({"MESSAGE_ID": DATABRIDGE_RESTART_WORKER}))
        self.jobs[name] = gevent.spawn(getattr(self, name))


def main():
    parser = argparse.ArgumentParser(description='Data Bridge')
    parser.add_argument('config', type=str, help='Path to configuration file')
    parser.add_argument('--tender', type=str, help='Tender id to sync', dest="tender_id")
    params = parser.parse_args()
    if os.path.isfile(params.config):
        config = SafeConfigParser()
        config.read(params.config)
        logging.config.fileConfig(params.config)
        bridge = DataBridge(config)
        bridge.launch()
    else:
        logger.info('Invalid configuration file. Exiting...')


if __name__ == "__main__":
    main()
