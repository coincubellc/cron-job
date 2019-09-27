import os
from time import sleep
import logging
import requests as rq
from database import db_session, ExPair

API_RETRIES = 5  # Times to retry query before giving up
GRACE_TIME = 5 # Seconds to sleep on exception

log = logging.getLogger(__name__)

_exapi_url = os.getenv('EXAPI_URL')

def get_request(endpoint, exchange, base, quote):
    for i in range(API_RETRIES + 1):
        try:
            url = _exapi_url + '/' + exchange + endpoint
            params = {'base' : base, 'quote' : quote}
            r = rq.get(url, params=params)
            log.debug(r.url)
            log.debug(r.status_code)
            r.raise_for_status()
            if r.status_code == 200:
                json_content = r.json()
                return json_content
        except Exception as e:
            if i == API_RETRIES:
                return None
            sleep(GRACE_TIME)


def remove_delisted_ex_pairs():
    ex_pairs = ExPair.query.filter_by(active=True).all()
    for ex_pair in ex_pairs:
        log.debug(f'{ex_pair} Checking if still listed')
        endpoint = '/history'
        price = get_request(
                    endpoint, 
                    ex_pair.exchange.name,
                    ex_pair.base_symbol,
                    ex_pair.quote_symbol
                    )
        if not price:
            log.debug(f'{ex_pair} possible delisting')

