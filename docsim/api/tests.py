from django.test import TestCase
from django.core.urlresolvers import reverse
import mox

from api import views


class MockSimServerTestCase(TestCase):
    '''Base class for API tests'''

    def setUp(self):
        super(MockSimServerTestCase, self).setUp()
        self.mox = mox.Mox()
        self.mox.StubOutWithMock(views, 'get_service')  # For safety

    def tearDown(self):
        super(MockSimServerTestCase, self).tearDown()
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    def mox_service(self):
        service = self.mox.CreateMockAnything()
        views.get_service().AndReturn(service)
        return service


class BufferHTMLDocTest(MockSimServerTestCase):

    def test_buffer_doc(self):
        post = {
            'id': 1,
            'html': '<p>a simple document</p>'
        }

        service = self.mox_service()
        service.buffer([{
            'id': '1',
            'tokens': ['simple', 'document']}])

        self.mox.ReplayAll()
        response = self.client.post(reverse('buffer_html'), post)
        self.mox.VerifyAll()

        self.assertEqual(response.status_code, 202)

    def test_bad_buffer_call(self):
        response = self.client.post(reverse('buffer_html'), {})
        self.assertEqual(response.status_code, 400)
