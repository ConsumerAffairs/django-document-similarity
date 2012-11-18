import logging

from django.conf import settings
from simserver import SessionServer
from sklearn.cluster import DBSCAN
from numpy import argwhere, identity

from .models import Cluster, Document

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class DocSimServer(object):
    def __init__(self):
        self.server = SessionServer(settings.SIMSERVER_WORKING_DIR)
        if not self.server.stable.model:
            self.server.train(self.corpus)
        if not self.server.stable.fresh_index:
            self.server.index(self.corpus)

    @property
    def corpus(self):
        try:
            return self._corpus
        except AttributeError:
            logging.info('creating corpus from DB')
            self._corpus = [dict(id=doc.id, tokens=doc.tokens())
                            for doc in Document.objects.all()]
            return self._corpus

    @property
    def document_ids(self):
        try:
            return self._document_ids
        except AttributeError:
            self._document_ids = list(
                Document.objects.values_list('id', flat=True).order_by('id'))
            return self._document_ids

    @property
    def index_id(self):
        try:
            return self._index_id
        except AttributeError:
            self._index_id = dict(enumerate(self.document_ids))
            return self._index_id

    @property
    def id_index(self):
        try:
            return self._id_index
        except AttributeError:
            self._id_index = dict((v, k) for k, v in self.index_id.iteritems())
            return self._id_index

    @property
    def similarity_matrix(self):
        try:
            return self._similarity_matrix
        except AttributeError:
            logging.info('calculating similarity matrix')
            s = identity(len(self.id_index))
            for id in self.document_ids:
                for sim_id, score, none in self.server.find_similar(
                        str(id), min_score=.2, max_results=10000):
                    if int(sim_id) != id:
                        s[self.id_index[id]][
                            self.id_index[int(sim_id)]] = score
            self._similarity_matrix = s
            return s

    @property
    def distance_matrix(self):
        try:
            return self._distance_matrix
        except AttributeError:
            s = self.similarity_matrix
            logging.info('converting similarity matrix to distance matrix')
            self._distance_matrix = 2 * (1 - s)
            return self._distance_matrix

    def dbscan_clusters(self, eps=.4, min_samples=5):
        D = self.distance_matrix
        logging.info('starting dbscan')
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
        db = dbscan.fit(D)
        labels = db.labels_
        clusters = [l for l in set(labels) if l > 0]  # outliers are -1
        logging.info('found %i clusters' % len(clusters))
        for c in clusters:
            cluster = Cluster(
                parameters=dict(algorithm='DBSCAN', eps=eps,
                                min_samples=min_samples))
            cluster.save()
            doc_ids = [self.index_id[i[0]] for i in argwhere(labels == c)]
            logging.info('cluster %s: %s documents' % (cluster.id, len(doc_ids)))
            cluster.documents.add(*doc_ids)
