from core import app
from functools import wraps
import unittest

class FlaskTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @staticmethod
    def withContext(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            with app.app_context():
                with app.test_request_context('/'):
                    fn(*args, **kwargs)
        return inner
