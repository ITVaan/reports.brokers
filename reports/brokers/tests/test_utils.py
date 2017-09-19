# -*- coding: utf-8 -*-
from unittest import TestCase
from pyramid import testing

import os
from reports.brokers.api.utils import *


class TestUtils(TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_read_user(self):
        with open('reports/brokers/tests/conf.ini', 'w+') as file:
            file.write('[SectionOne]\nStatus: 111\n\n[SectionTwo]\nStatus: 123')
        self.assertEqual(read_users('reports/brokers/tests/conf.ini'), None)
        os.remove('reports/brokers/tests/conf.ini')

    def test_request_params(self):
        request = testing.DummyRequest()
        self.assertEqual(request_params(request), NestedMultiDict())

    def test_request_params_exception(self):
        request = testing.DummyRequest().response
        self.assertRaises(Exception, lambda: request_params(request))
