# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import logging.config

import requests
from requests import RequestException
from retrying import retry

logger = logging.getLogger(__name__)


class DocServiceClient(object):
    """Base class for making requests to Document Service"""

    def __init__(self, host, port=6555, timeout=None):
        self.session = requests.Session()
        self.url = u'{host}:{port}/upload'.format(host=host, port=port)
        self.timeout = timeout
        self.headers = {}

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1)
    def download(self, url):
        res = self.session.get(url=url, timeout=self.timeout)
        if res.status_code == 200:
            return res.content
        else:
            raise RequestException(res)
