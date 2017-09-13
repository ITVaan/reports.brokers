# -*- coding: utf-8 -*-
from collections import namedtuple
from logging import getLogger
from uuid import uuid4

from restkit import ResourceError

LOGGER = getLogger(__name__)

EdrDocument = namedtuple("EdrDocument", ['tender_id', 'bid_id', 'document_url'])


def journal_context(record={}, params={}):
    for k, v in params.items():
        record["JOURNAL_" + k] = v
    return record


def generate_req_id():
    return b'data-bridge-req-' + str(uuid4()).encode('ascii')


def check_412(func):
    def func_wrapper(obj, *args, **kwargs):
        try:
            response = func(obj, *args, **kwargs)
        except ResourceError as re:
            if re.status_int == 412:
                obj.headers['Cookie'] = re.response.headers['Set-Cookie']
                response = func(obj, *args, **kwargs)
            else:
                raise ResourceError(re)
        return response

    return func_wrapper


def more_tenders(params, response):
    return not (params.get('descending')
                and not len(response.data) and params.get('offset') == response.next_page.offset)
