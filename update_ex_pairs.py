import requests
from database import *


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

BASE_URL = os.getenv('EXAPI_URL')


def get_markets(exchange_name):
    url = BASE_URL + exchange_name + '/markets'
    response = requests.get(url)
    response.raise_for_status()
    json_content = response.json()
    return json_content

def update_eps():
    try:
        for ex in Exchange.query.filter_by(active=True).all():

            log.info(f'Updating ex_pairs for {ex.name}.')

            missing_curs = []

            try:
                log.debug('Get markets (API)')
                exchange = '/' + ex.name
                markets = get_markets(exchange)
                if not markets:
                    continue
            except AttributeError:
                continue
            except Exception as e:
                log.info('%s: %s' % (ex.name, e))
                continue

            # Add missing ex_pairs
            log.info(f'Adding missing ex_pairs for {ex.name}.')
            for market in markets:

                base, quote = market.split('/')

                base_cur = Currency.query.filter_by(symbol=base).first()
                quote_cur = Currency.query.filter_by(symbol=quote).first()

                if not base_cur:
                    missing_curs.append(base)
                    continue
                if not quote_cur:
                    missing_curs.append(quote)
                    continue

                # Filter out stable coins in base
                if base_cur.symbol in ['USD', 'EUR', 'USDT', 'TUSD', 'USDC', 'USDS', 'GUSD', 'PAX']:
                    continue

                ep = ExPair.query.filter_by(exchange=ex, base_currency=base_cur, quote_currency=quote_cur).first()
                if ep:
                    # expair already exists
                    if ep.active == False:
                        ep.active = True
                        log.info(f'Setting ex_pair to active: {ep}')
                        db_session.add(ep)
                    continue

                ep = ExPair(
                  exchange=ex,
                  base_currency=base_cur,
                  quote_currency=quote_cur,
                  base_symbol=base,
                  quote_symbol=quote,
                  active=True
                  )
                db_session.add(ep)
                log.info(f'Creating ex_pair: {ep}')
            if missing_curs:
                log.debug('Missing currencies for %s: %s' % (ex.name, ' '.join(missing_curs)))

            db_session.commit()

            # Removing unsupported ex_pairs
            log.info(f'Removing unsupported ex_pairs for {ex.name}.')
            ex_pairs = ExPair.query.filter_by(exchange=ex).all()
            for ep in ex_pairs:
                if ep.active == True:
                    symbol = f'{ep.base_symbol}/{ep.quote_symbol}'
                    if symbol not in markets:
                        log.debug(f'Setting {symbol} to inactive: No longer supported on {ex.name}.')
                        ep.active = False
                        ep.save_to_db()
    except Exception as e:
        log.error(e)


if __name__ == '__main__':
    update_eps()