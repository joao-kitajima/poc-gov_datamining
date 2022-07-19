import datetime
import logging

import azure.functions as func
from config.definitions import run_spider, upload
from scraping.scraping.spiders import crawlers


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    
    # Running Spiders
    run_spider(spider=crawlers.AlmgCrawler, crawler=True)
    upload(crawler=True)
