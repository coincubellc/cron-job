import os
import requests
from decimal import Decimal as dec
from database import (db_session, ExPair, ExPairClose,
                      IndexPair, IndexPairClose, log)

_exapi_url = os.getenv('EXAPI_URL')


def get_price(exchange, base, quote):
    url = f'{_exapi_url}/{exchange}/midprice'
    params = {'base': base, 'quote': quote}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        price = r.json()
        return dec(price['price_str'])
    else:
        raise r.status_code

def update_ex_pair_close():
    log.debug('Updating ExPairClose')
    ex_pairs = ExPair.query.filter_by(active=True).all()

    for ex_pair in ex_pairs:
        log.debug(f'Updating close for {ex_pair}')
        epc = ExPairClose.query.filter_by(
                                ex_pair_id=ex_pair.id
                                ).first()
        try:
            close = get_price(ex_pair.exchange.name, ex_pair.base_symbol, ex_pair.quote_symbol)
            log.debug(close)
        except:
            close = 0
        if not epc:
            epc = ExPairClose(
                    ex_pair_id=ex_pair.id,
                    close=close,
                )
            db_session.add(epc)
            db_session.commit()
            continue

        epc.close = close
        log.debug(f'Updated close for {epc}')
        db_session.add(epc)
        db_session.commit()
    log.debug('Finished Updating ExPairClose')

def update_index_pair_close():
    log.debug('Updating IndexPairClose')
    index_pairs = IndexPair.query.filter_by(active=True).all()

    for index_pair in index_pairs:
        # Get all related, active and non-External ExPairs
        ex_pairs = ExPair.query.filter(
            ExPair.quote_currency_id == index_pair.quote_currency_id,
            ExPair.base_currency_id == index_pair.base_currency_id,
            ExPair.active == True,
        ).all()

        if not ex_pairs:
            log.info(f"No exchange pairs available for {index_pair}.")
            continue

        # Average of exchanges for close
        total_close = 0
        for ex_pair in ex_pairs:
            total_close += ex_pair.get_close()

        total_close /= len(ex_pairs)

        log.debug(f'Updating close for {index_pair}')
        ipc = IndexPairClose.query.filter_by(
                                ex_pair_id=index_pair.id
                                ).first()

        if not ipc:
            ipc = IndexPairClose(
                    ex_pair_id=index_pair.id,
                    close=total_close,
                )
            db_session.add(ipc)
            db_session.commit()
            continue

        ipc.close = total_close
        log.debug(f'Updated close for {ipc}')
        db_session.add(ipc)
        db_session.commit()
    log.debug('Finished Updating IndexPairClose')

def update_close():
    try:
        update_ex_pair_close()
        update_index_pair_close()
    except Exception as e:
        log.error(e)