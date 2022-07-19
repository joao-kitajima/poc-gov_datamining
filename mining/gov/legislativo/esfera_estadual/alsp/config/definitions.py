import json
import os
from multiprocessing import Process, Queue

from azure.storage.blob import ContainerClient
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor


# Filepath constant of current project
ROOT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '../'))


def build_filepath(file: str) -> str:
    """Pass __file__ name and get the absolute filepath."""
    
    return os.path.join(ROOT_DIR, file)


def get_project_name() -> str:
    """Get the current project's folder name."""
    
    return os.getcwd().split('/')[-1]


# Azure Connection
def get_connection_string() -> str:
    """Get Azure Web Jobs Storage Key from 'local.settings.json'."""
    
    with open(build_filepath('local.settings.json')) as file:
        return json.load(file)['Values']['AzureWebJobsStorage']


# Spider Configs
def run_spider(spider: Spider, settings: dict=None, crawler=False) -> None:
    CRAWLER_SETTINGS = {
        'FEEDS': {
            f'temp/{get_project_name()}_crawler.jsonl': {
                'format': 'jsonlines',
                'encoding': 'utf8',
                'overwrite': True
            }
        }
    }
    
    def f(q, settings=settings, crawler=crawler):
        try:
            if crawler:
                runner = CrawlerRunner(settings=CRAWLER_SETTINGS)
            else:
                runner = CrawlerRunner(settings)
            
            deferred = runner.crawl(spider)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    queue = Queue()
    process = Process(target=f, args=(queue,))
    process.start()
    result = queue.get()
    process.join()

    if result is not None:
        raise result
    

# Upload Configs
def upload(crawler=False):
    def get_files():
        dir = build_filepath('temp/')
    
        with os.scandir(dir) as entries:
            for entry in entries:
                if entry.is_file() \
                    and not entry.name == 'README.md' \
                    and not entry.name.startswith('.'):
                        yield entry
    
    if crawler:
        container_client = ContainerClient.from_connection_string(
            get_connection_string(), 'datasources')  
    else:
        container_client = ContainerClient.from_connection_string(
            get_connection_string(), 'datalake')
        
    print('Uploading files to blob storage ...')
    
    for file in get_files():
        blob_client = container_client.get_blob_client(file.name)
        
        with open(file.path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
            os.remove(file)            
            print('Data uploaded to blob storage.')
