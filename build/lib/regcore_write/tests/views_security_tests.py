import base64

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from regcore_write.views import security


def _wrapped_fn(request):
    return HttpResponse(status=204)


def _encode(username, password):
    as_unicode = '{0}:{1}'.format(username, password).encode()
    encoded = base64.b64encode(as_unicode).decode('utf-8')
    return 'Basic ' + encoded


class SecurityTest(TestCase):
    @override_settings(HTTP_AUTH_USER="a_user", HTTP_AUTH_PASSWORD="a_pass")
    def test_secure_write(self):
        """Basic Auth must match the configuration"""
        fn = security.secure_write(_wrapped_fn)

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

    @override_settings(HTTP_AUTH_USER=None, HTTP_AUTH_PASSWORD=None)
    def test_secure_write_unset(self):
        """Basic Auth should not be required when the environment isn't set"""
        fn = security.secure_write(_wrapped_fn)
        request = RequestFactory().get('/')
        self.assertEqual(fn(request).status_code, 204)

    @override_settings(HTTP_AUTH_USER="", HTTP_AUTH_PASSWORD="")
    def test_secure_write_empty(self):
        """Basic Auth should not be required when the environment is empty"""
        fn = security.secure_write(_wrapped_fn)
        request = RequestFactory().get('/')
        self.assertEqual(fn(request).status_code, 204)
