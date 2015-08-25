import base64

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from regcore_write.views import security


def _wrapped_fn(request):
    return HttpResponse(status=204)


def _encode(username, password):
    encoded = base64.b64encode('{}:{}'.format(username, password))
    return 'Basic ' + encoded


class SecurityTest(TestCase):
    @override_settings(HTTP_AUTH_USER="a_user", HTTP_AUTH_PASSWORD="a_pass")
    def test_basic_auth(self):
        """Basic Auth must match the configuration"""
        fn = security.basic_auth(_wrapped_fn)

        request = RequestFactory().get('/')
        self.assertEqual(fn(request).status_code, 401)

        request = RequestFactory().get(
            '/', HTTP_AUTHORIZATION=_encode('wrong', 'pass'))
        self.assertEqual(fn(request).status_code, 401)

        request = RequestFactory().get(
            '/', HTTP_AUTHORIZATION=_encode('a_user', 'pass'))
        self.assertEqual(fn(request).status_code, 401)

        request = RequestFactory().get(
            '/', HTTP_AUTHORIZATION=_encode('wrong', 'a_pass'))
        self.assertEqual(fn(request).status_code, 401)

        request = RequestFactory().get(
            '/', HTTP_AUTHORIZATION=_encode('a_user', 'a_pass'))
        self.assertEqual(fn(request).status_code, 204)
