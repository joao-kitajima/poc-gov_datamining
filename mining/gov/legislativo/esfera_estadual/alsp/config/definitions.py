import os
from multiprocessing import Process, Queue
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor


ROOT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..'))


def run_spider(spider, settings={
        'FEEDS': {
            'alsp_crawler.jsonl': {
                'format': 'jsonlines',
                'encoding': 'utf8',
                'overwrite': True
            }
        }
    }):
    def f(q):
        try:
            runner = CrawlerRunner(settings=settings)
            deferred = runner.crawl(spider)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
