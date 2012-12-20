# -*- encoding: utf-8 -*-
from json import loads

from django.test import TestCase
from django.core.urlresolvers import reverse
import mox

from .docsimserver import DocSimServer
from .models import Cluster, Document
from .tokenizers import force_ascii


class MockTestCase(TestCase):
    '''Base class for tests needing mock'''

    def setUp(self):
        super(MockTestCase, self).setUp()
        self.mox = mox.Mox()

    def tearDown(self):
        super(MockTestCase, self).tearDown()
        self.mox.VerifyAll()
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


class ViewAddOrUpdateTest(TestCase):

    def test_add_doc(self):
        post = {
            'id': 1,
            'text': '<p>a simple document</p>'
        }
        self.assertFalse(Document.objects.exists())

        response = self.client.post(reverse('add_or_update'), post)

        self.assertEqual(response.status_code, 202)
        doc = Document.objects.get()
        self.assertEqual(doc.id, str(post['id']))
        self.assertEqual(doc.text, post['text'])

    def test_update_doc(self):
        Document.objects.create(id='3', text='foobar')
        post = {
            'id': 3,
            'text': '<p>baz</p>'
        }

        response = self.client.post(reverse('add_or_update'), post)

        self.assertEqual(response.status_code, 202)
        doc = Document.objects.get()
        self.assertEqual(doc.id, str(post['id']))
        self.assertEqual(doc.text, post['text'])

    def test_bad_request(self):
        response = self.client.post(reverse('add_or_update'), {})
        self.assertEqual(response.status_code, 400)


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
    def test_empty_post(self):
        response = self.client.post(reverse('find-similar'), {})
        self.assertEqual(response.status_code, 400)

    def test_text(self):
        self.mox.StubOutWithMock(DocSimServer, '__init__')
        self.mox.StubOutWithMock(DocSimServer, 'find_similar')
        DocSimServer.__init__()
        DocSimServer.find_similar(
            {'tokens': ['test']}, max_results=10, min_score=.8).AndReturn(
            [("test_document:1", 0.8776240944862366, None),
             ("test_document:2", 0.8762409448623661, None),
             ("test_document:3", 0.7762409448623668, None)])
        self.mox.ReplayAll()
        response = self.client.post(reverse('find-similar'), {'text': 'test'})
        self.assertEqual(
            response.content, 
            '[["test_document:1",0.87762,null],'
            '["test_document:2",0.87624,null],'
            '["test_document:3",0.77624,null]]')
