import datetime
import logging
import os
import azure.functions as func
from io import TextIOWrapper
from config.definitions import ROOT_DIR, run_spider, upload, get_files, load_yaml_config
from scraping.scraping.spiders import crawlers


def main(mytimer: func.TimerRequest, outputblob: func.Out[TextIOWrapper]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    
    # Running Crawler
    run_spider(spider=crawlers.AlspCrawler)
    
    config = load_yaml_config()
    scraped_data = get_files(config['source_folder'] + '/data')
    upload(scraped_data, config['azure_storage_connectionstring'], config['datalake'])
    