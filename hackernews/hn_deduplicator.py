'''
Created on May 22, 2015

@author: sprasa7
'''
from bs4 import BeautifulSoup
import urllib2
from logging import info, debug, error, INFO, getLogger
import logging
#from nltk.corpus import stopwords

logging.basicConfig(level=INFO)
getLogger('dedup').setLevel(INFO)

HN_URL = "https://news.ycombinator.com/news?"

#cachedStopWords = stopwords.words("english")

class Article(object):

    def __init__(self, url, text):
        self.url = url
        self.text = text

    def __str__(self):
        return str(self.url)

    def __eq__(self, other):
        return self.url == other.url

class DuplicateArticlePair(object):

    def __init__(self, articleA, articleB):
        self.articleA = articleA
        self.articleB = articleB

    def __str__(self):
        return "(" + str(self.articleA) + " , " + str(self.articleB) + ")"

    def __eq__(self, other):
        return ( self.articleA == other.articleA and self.articleB == other.articleB ) or ( self.articleA == other.articleB and self.articleB == other.articleA )

def compute_jaccard_index(set_1, set_2):
    return len(set_1.intersection(set_2)) / float(len(set_1.union(set_2)))

def are_duplicates(articleA, articleB):
    #cleaned_articleA = ' '.join([word for word in articleA.split() if word not in cachedStopWords])
    #cleaned_articleB = ' '.join([word for word in articleB.split() if word not in cachedStopWords])

    set_1 = set(articleA.lower().split(" "))
    set_2 = set(articleB.lower().split(" "))
    score = compute_jaccard_index(set_1, set_2)
    if score > 0.2:
        debug("Jaccard score for [%s, %s] = > %f", articleA, articleB, score)
    if score > 0.5:
        info("Jaccard score for [%s, %s] = > %f", articleA, articleB, score)
        return True

    return False

def find_duplicates(articles):
    duplicates = []
    for article_outer in sorted(articles):
        debug("Analyzing article : %s", article_outer)
        for article_inner in articles:
            debug("Comparing %s with %s", article_inner.text, article_outer.text)
            if article_outer.text == article_inner.text:
                continue

            if are_duplicates(article_outer.text, article_inner.text):
                dup_pair = DuplicateArticlePair(article_outer, article_inner)
                duplicates.append(dup_pair)
                debug("Duplicate Pair : %s", str(dup_pair))

    return set(duplicates)

def get_articles_to_analyze(url):
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    articles = soup.findAll('td', {'class' : 'title'})

    article_list = []
    for article_wrapper in articles:
        for article_url in article_wrapper.find_all('a', href=True):
            article_header = article_url.text
            if not is_hn_article_to_be_skipped(article_header):
                article_list.append(Article(article_url, article_header))

    info("Found %d articles for url %s", len(article_list), url)
    return article_list

def is_hn_article_to_be_skipped(article_header):
    if article_header == "More" or "Show HN:" in article_header or "Ask HN:" in article_header:
        return True

    return False

if __name__ == '__main__':
    articles = []
    count = 0
    for index in range(1,25):
        try:
            url = HN_URL + "p=" + str(index)
            index_articles = get_articles_to_analyze(url)
            articles.extend(index_articles)

            count +=1
        except Exception, e:
            error("Failed for index %d. Reason => %s", index, str(e))

    duplicates = find_duplicates(articles)
    info("Found %d duplicates in top %d HN pages", len(duplicates), count)
    for duplicate in duplicates:
        info("%s", str(duplicate))

