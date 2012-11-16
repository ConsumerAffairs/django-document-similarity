import chardet
import nltk
import re


# from nltk.corpus.stopwords.words('english') + a few others
stopwords = [
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an',
    'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before',
    'being', 'below', 'between', 'both', 'but', 'by', 'can', 'did', 'do',
    'does', 'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from',
    'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers',
    'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is',
    'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', "n't",
    'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 's', 'same',
    'she', 'should', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their',
    'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was',
    'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
    'why', 'will', 'with', 'would', 'you', 'your', 'yours', 'yourself',
    'yourselves']

word_regex = re.compile(r'\w+')


def force_ascii(s):
    if isinstance(s, str):
        try:
            return unicode(s, 'ascii', errors='ignore')
        except:
            try:
                s = unicode(s.decode(chardet.detect(s)['encoding']))
            finally:
                return s.encode('ascii', 'ignore')
    elif isinstance(s, unicode):
        return s.encode('ascii', 'ignore')


def tokenize_html_generator(html):
    cleaned = nltk.clean_html(force_ascii(html.lower()))
    for sentence in nltk.tokenize.sent_tokenize(cleaned):
        for token in nltk.tokenize.word_tokenize(sentence):
            if word_regex.match(token) and token not in stopwords:
                yield token


def tokenize_html(html):
    return list(tokenize_html_generator(html))
