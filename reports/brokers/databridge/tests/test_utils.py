# -*- coding: utf-8 -*-
from unittest import TestCase

from mock import MagicMock
from reports.brokers.databridge.utils import check_412
from restkit import ResourceError


class TestUtils(TestCase):
    def test_check_412_function(self):
        func = check_412(MagicMock(side_effect=ResourceError(
            http_code=412, response=MagicMock(headers={'Set-Cookie': 1}))))
        with self.assertRaises(ResourceError):
            func(MagicMock(headers={'Cookie': 1}))
        func = check_412(MagicMock(side_effect=ResourceError(
            http_code=403, response=MagicMock(headers={'Set-Cookie': 1}))))
        with self.assertRaises(ResourceError):
            func(MagicMock(headers={'Cookie': 1}))
        f = check_412(MagicMock(side_effect=[1]))
        self.assertEqual(f(1), 1)
