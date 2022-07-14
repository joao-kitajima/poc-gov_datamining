import datetime
import logging
import os
import azure.functions as func
from io import TextIOWrapper
from config.definitions import ROOT_DIR, run_spider
from ..scraping.scraping.spiders import crawlers


def main(mytimer: func.TimerRequest, outputblob: func.Out[TextIOWrapper]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    
    # Running Crawler
    run_spider(spider=crawlers.AlspCrawler)
    
    with open(os.path.join(ROOT_DIR, 'alsp_crawler.jsonl')) as file_handler:
        content = file_handler.read()
        outputblob.set(content)
