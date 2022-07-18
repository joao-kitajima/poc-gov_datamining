import os
from multiprocessing import Process, Queue
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
import yaml
from azure.storage.blob import ContainerClient


ROOT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..'))


def run_spider(spider, settings={
        'FEEDS': {
            'data/alsp_crawler.jsonl': {
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

    queue = Queue()
    process = Process(target=f, args=(queue,))
    process.start()
    result = queue.get()
    process.join()

    if result is not None:
        raise result
    
    
def load_yaml_config():
    dir_root = os.path.dirname(os.path.abspath(__file__))
    
    with open(dir_root + '/config.yaml') as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)


def get_files(dir):
    with os.scandir(dir) as entries:
        for entry in entries:
            if entry.is_file() \
                and not entry.name.startswith('.') \
                and not entry.name == 'README.md':
                    yield entry
                

def upload(files, connection_string, container_name, rmdir=True):
    container_client = ContainerClient.from_connection_string(connection_string, container_name)
    print('Uploading files to blob storage ...')
    
    for file in files:
        blob_client = container_client.get_blob_client(file.name)
        
        with open(file.path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
            print('Data uploaded to blob storage.')
            
            if rmdir:
                os.remove(file)
                
                
config = load_yaml_config()
sc_data = get_files(config['source_folder'] + '/data')
print(* sc_data)
                

