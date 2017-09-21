# -*- coding: utf-8 -*-

from gevent import monkey

monkey.patch_all()

import gevent
import logging.config

from gevent import spawn
from gevent.queue import Queue
from yaml import load as load_yaml
from requests import RequestException

from reports.brokers.databridge.base_worker import BaseWorker

logger = logging.getLogger(__name__)


class DownloadFromDocServiceWorker(BaseWorker):
    """ Data Bridge """

    def __init__(self, services_not_available, doc_client, items_to_download_queue, edr_data_to_database):
        super(DownloadFromDocServiceWorker, self).__init__(services_not_available)
        self.items_to_download_queue = items_to_download_queue
        self.edr_data_to_database = edr_data_to_database
        self.doc_client = doc_client
        self.retry_items_to_download_queue = Queue(500)

    def get_item_from_doc_service(self):
        while not self.exit:
            self.temp_action()
            gevent.sleep()

    def temp_action(self):
        data = self.items_to_download_queue.get()
        document = self.try_to_get_data(data)
        if document:
            res_data = (data.tender_id, data.bid_id, document)
            # TODO: won't go anywhere because putting into db is not ready yet:
            self.edr_data_to_database.put(res_data)
            logger.info("Have put item into database: {}_{}. Queue size: {}".format(data.tender_id, data.bid_id, self.edr_data_to_database.qsize()))
        else:
            self.retry_items_to_download_queue.put(data)

    def try_to_get_data(self, data):
        try:
            res = self.doc_client.download(data.document_url)
            raw = res.raw.read()
            return load_yaml(raw)
        except RequestException as e:
            logger.info("Exception happened while trying to download: {}".format(e))
        except Exception as e:
            logger.info("Unknown exception happened. {}".format(e))

    def retry_get_item_from_doc_service(self):
        while not self.exit:
            self.retry_temp_action()
            gevent.sleep()

    def retry_temp_action(self):
        data = self.retry_items_to_download_queue.peek()
        document = self.try_to_get_data(data)
        if document:
            res_data = (data.tender_id, data.bid_id, document)
            self.edr_data_to_database.put(res_data)
            self.retry_items_to_download_queue.get()
        else:
            self.retry_items_to_download_queue.put(self.retry_items_to_download_queue.get())

    def _start_jobs(self):
        return {'get_item_from_doc_service': spawn(self.get_item_from_doc_service),
                'retry_get_item_from_doc_service': spawn(self.retry_get_item_from_doc_service)}
