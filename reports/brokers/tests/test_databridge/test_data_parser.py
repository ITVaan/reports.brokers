# coding=utf-8
import json
from unittest import TestCase

import hypothesis.strategies as st
from hypothesis import given
from mock import MagicMock

from reports.brokers.databridge.data_parser import JSONDataParser

test_award = st.one_of(st.none(), st.fixed_dictionaries({
    u"id": st.text(),
    u"bid_id": st.text(),
    u"documents": st.lists(st.fixed_dictionaries({"url": st.text()}))
}),
                       st.fixed_dictionaries({
                           u"id": st.text(),
                           u"documents": st.lists(st.fixed_dictionaries({"url": st.text()}))
                       }
                       ))

test_data = st.fixed_dictionaries({
    u"id": st.text(),
    u"awards": st.lists(test_award)
})

test_data_in = st.one_of(st.none(), test_data, st.fixed_dictionaries({
    "data": test_data
}), st.fixed_dictionaries({
    u"data": test_data
}))

test_response_body = st.text(test_data)


class JSONDataParserTest(TestCase):
    def setUp(self):
        pass

    def test_init(self):
        json_parser = JSONDataParser()

    @given(test_data)
    def test_processing_docs(self, tender_data):
        json_parser = JSONDataParser()
        edr_doc = json_parser.processing_docs(tender_data)

    @given(test_data_in)
    def test_process_items_and_move(self, tender_data):
        json_parser = JSONDataParser()
        response = MagicMock(body_string=MagicMock(return_value=json.dumps(tender_data)))
        edr_doc = json_parser.process_items_and_move(response)
