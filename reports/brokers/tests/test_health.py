from unittest import TestCase
from pyramid import testing
from reports.brokers.api.views.health import health


class TestHealth(TestCase):
    """ Test health view"""

    def test_health(self):
        request = testing.DummyRequest()
        self.assertEqual(health(request), '')
