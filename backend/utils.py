
import logging
import os


def create_scrape_data(listing_url: str = '', listing_id: str = '', keyword: str = '', http_status_code: str = '') -> dict:
    data = {
        'KEYWORD': keyword,
        'LINK': listing_url,
        'ERANK_URL': "https://erank.com/listing-audit/{}".format(listing_id),
        'VISIBILITY_SCORE': '',
        'DAILY_VIEWS': '',
        'LISTING_AGE': '',
        'LISTING_ID': listing_id,
        'HTTP_STATUS_CODE': http_status_code,
        'ERROR': ''
    }
    return data


def buildLogger(file_name: str = 'app.log'):
    # Create and configure logger
    logging.basicConfig( filename=os.path.join('static', 'log_'+file_name+'.log'),
        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
         filemode='w'
    )

    # Creating an object
    logger = logging.getLogger(file_name)

    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)

    return logger
