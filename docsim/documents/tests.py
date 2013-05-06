# -*- encoding: utf-8 -*-
from json import loads

from django.test import TestCase
from django.core.urlresolvers import reverse
import mox

from .docsimserver import DocSimServer
from .models import Cluster, Document
from .tokenizers import force_ascii
from documents import views


class MockTestCase(TestCase):
    '''Base class for tests needing mock'''

    def setUp(self):
        super(MockTestCase, self).setUp()
        self.mox = mox.Mox()

    def tearDown(self):
        super(MockTestCase, self).tearDown()
        self.mox.UnsetStubs()


class ModelDocumentTest(TestCase):
    def test_str(self):
        doc = Document.objects.create(id='1', text='foo')
        self.assertEqual(str(doc), '1')

    def test_str_integer_id(self):
        doc = Document.objects.create(id=1, text='foo')
        self.assertEqual(str(doc), '1')

    def test_tokenize_html(self):
        doc = Document.objects.create(
            id=1, text='<p>a simple document</p>')
        self.assertEqual(doc.tokens(), ['simple', 'document'])


class TokenizerForceAsciiTest(TestCase):
    def test_plain_string(self):
        test = 'This is a plain string'
        self.assertEqual(test, force_ascii(test))

    def test_plain_unicode(self):
        test = u'This is a unicode string'
        self.assertEqual(str(test), force_ascii(test))

    def test_latin1_as_utf8(self):
        test = unicode('latin-1 is the bömb', 'latin-1').encode('utf-8')
        expected = 'latin-1 is the bmb'
        self.assertEqual(expected, force_ascii(test))


class ViewAddOrUpdateTest(MockTestCase):

    def test_add_doc(self):
        post = {'id': 1, 'text': '<p>a simple document</p>'}
        self.assertFalse(Document.objects.exists())

        response = self.client.post(reverse('add_or_update'), post)

        self.assertEqual(response.status_code, 202)
        doc = Document.objects.get()
        self.assertEqual(doc.id, str(post['id']))
        self.assertEqual(doc.text, post['text'])

    def test_update_doc(self):
        Document.objects.create(id='3', text='foobar')
        post = {'id': 3, 'text': '<p>baz</p>'}

        response = self.client.post(reverse('add_or_update'), post)

        self.assertEqual(response.status_code, 202)
        doc = Document.objects.get()
        self.assertEqual(doc.id, str(post['id']))
        self.assertEqual(doc.text, post['text'])

    def test_bad_request(self):
        response = self.client.post(reverse('add_or_update'), {})
        self.assertEqual(response.status_code, 400)

    def test_index(self):
        self.mox.StubOutWithMock(views, 'dss')
        dss = self.mox.CreateMockAnything()
        dss.server = self.mox.CreateMockAnything()
        dss.server.index(
            [{'tokens': ['test'], 'id': 'test_document:4'}])
        views.dss().AndReturn(dss)
        self.mox.ReplayAll()
        post = {'id': 'test_document:4', 'text': 'test', 'index': True}
        self.assertFalse(Document.objects.exists())
        response = self.client.post(reverse('add_or_update'), post)
        self.mox.VerifyAll()
        self.assertEqual(response.status_code, 202)
        doc = Document.objects.get()
        self.assertEqual(doc.id, str(post['id']))
        self.assertEqual(doc.text, post['text'])


class ClusterModelTest(TestCase):
    def test_unicode(self):
        cluster = Cluster()
        self.assertEqual(unicode(cluster), '{}')
        cluster.parameters['test'] = True
        self.assertEqual(unicode(cluster), '{"test": true}')


class APITest(TestCase):
    def setUp(self):
        self.doc1 = Document.objects.create(
            id='test_document:1', text='testdoc1')
        self.doc2 = Document.objects.create(
            id='test_document:2', text='testdoc2')
        self.cluster = Cluster.objects.create()
        self.cluster.documents.add(self.doc1, self.doc2)

    def test_get_cluster_list(self):
        response = self.client.get(reverse('cluster-list'))
        loaded = loads(response.content)
        self.assertEqual(loaded[0]['id'], 1)
        self.assertTrue(self.doc1.id in loaded[0]['documents'])
        self.assertTrue(self.doc2.id in loaded[0]['documents'])

    def test_get_cluster_detail(self):
        response = self.client.get(reverse('cluster-detail', args=(1,)))
        loaded = loads(response.content)
        self.assertEqual(loaded['id'], 1)
        self.assertTrue(self.doc1.id in loaded['documents'])
        self.assertTrue(self.doc2.id in loaded['documents'])


class FindSimilarTest(MockTestCase):
    def setUp(self):
        super(FindSimilarTest, self).setUp()
        self.mox.StubOutWithMock(views, 'dss')

    def test_empty_get(self):
        self.mox.ReplayAll()
        response = self.client.get(reverse('find-similar'), {})
        self.mox.VerifyAll()
        self.assertEqual(response.status_code, 400)

    def test_get_invalid_id(self):
        dss = self.mox.CreateMockAnything()
        dss.find_similar('foo', max_results=10, min_score=0.8).AndRaise(ValueError)
        views.dss().AndReturn(dss)
        self.mox.ReplayAll()
        response = self.client.get(
            reverse('find-similar'), {'id': 'foo'})
        self.mox.VerifyAll()
        self.assertEqual(response.status_code, 400)

    def test_get_invalid_min_score(self):
        self.mox.ReplayAll()
        response = self.client.get(
            reverse('find-similar'), {'id': 'foo', 'min_score': 'bar'})
        self.mox.VerifyAll()
        self.assertEqual(response.status_code, 400)

    def test_get_invalid_max_results(self):
        self.mox.ReplayAll()
        response = self.client.get(
            reverse('find-similar'), {'id': 'foo', 'max_results': 'bar'})
        self.mox.VerifyAll()
        self.assertEqual(response.status_code, 400)

    def test_empty_post(self):
        self.mox.ReplayAll()
        response = self.client.post(reverse('find-similar'), {})
        self.mox.VerifyAll()
        self.assertEqual(response.status_code, 400)

    def test_text(self):
        dss = self.mox.CreateMockAnything()
        views.dss().AndReturn(dss)
        dss.find_similar(
            {'tokens': ['test']}, max_results=10, min_score=0.8).AndReturn(
                [("test_document:1", 0.8776240944862366, None),
                 ("test_document:2", 0.8762409448623661, None),
                 ("test_document:3", 0.7762409448623668, None)])
        self.mox.ReplayAll()
        response = self.client.post(reverse('find-similar'), {'text': 'test'})
        self.mox.VerifyAll()
        self.assertEqual(
            response.content,
            '[["test_document:1",0.87762,null],'
            '["test_document:2",0.87624,null],'
            '["test_document:3",0.77624,null]]')

#    def test_text_and_update(self):
#        dss = self.mox.CreateMockAnything()
#        dss.server = self.mox.CreateMockAnything()
#        dss.server.index(
#            [{'tokens': ['test'], 'id': 'test_document:4'}])
#        dss.find_similar(
#            "test_document:4", max_results=10, min_score=0.8).AndReturn(
#                [("test_document:1", 0.8776240944862366, None),
#                 ("test_document:2", 0.8762409448623661, None),
#                 ("test_document:3", 0.7762409448623668, None)])
#        views.dss().AndReturn(dss)
#        views.dss().AndReturn(dss)
#        self.mox.ReplayAll()
#        response = self.client.post(reverse('find-similar'),
#                                    {'text': 'test', 'id': 'test_document:4'})
#        self.mox.VerifyAll()
#        self.assertEqual(
#            response.content,
#            '[["test_document:1",0.87762,null],'
#            '["test_document:2",0.87624,null],'
#            '["test_document:3",0.77624,null]]')
#        doc4 = Document.objects.get()
#        self.assertEqual(doc4.id, 'test_document:4')
