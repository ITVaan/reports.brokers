# -*- coding: utf-8 -*-
from unittest import TestCase
from reports.brokers.api.auth import authenticated_role
from mock import MagicMock


class TestAuth(TestCase):
    def test_authenticated_role(self):
        request = MagicMock()
        self.assertEqual(authenticated_role(request), 'anonymous')
