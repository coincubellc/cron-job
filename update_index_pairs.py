import logging
from database import (Currency, ExPair, IndexPair, db_session)

log = logging.getLogger(__name__)


def update_ips():
    """ Creates index pairs (if necessary) for all individual ExPairs.
    """
    log.debug("Updating IndexPair table")
    # Query for all Currencies
    all_curs = Currency.query.all()
    # Quote currencies: BTC, USD, EUR
    quote_curs = Currency.query.filter(Currency.symbol.in_(['BTC', 'USD', 'EUR', 'USDT', 'TUSD', 'USDC', 'USDS', 'GUSD', 'PAX'])).all()

    try:
        for quote_cur in quote_curs:
            for base_cur in all_curs:
                if base_cur.symbol in ['USD', 'EUR', 'USDT', 'TUSD', 'USDC', 'USDS', 'GUSD', 'PAX']:
                    # Don't want USDT/BTC or similar
                    continue
                if quote_cur == base_cur:
                    continue
                # Check for any ExPair for given base/quote
                ex_pair = ExPair.query.filter_by(
                    quote_currency_id=quote_cur.id,
                    base_currency_id=base_cur.id,
                    active=True).first()

                # ExPair exists, so we need a matching IndexPair
                index_pair = IndexPair.query.filter_by(
                    quote_currency_id=quote_cur.id,
                    base_currency_id=base_cur.id
                ).first()

                if not ex_pair and index_pair:
                    # No matching ex_pair, setting index_pair to inactive
                    index_pair.active = False
                    index_pair.save_to_db()
                    continue

                if not ex_pair:
                    continue

                if index_pair:  # IndexPair already exists
                    continue
                else:
                    log.debug("Adding missing IndexPair for %s/%s" %
                              (base_cur.symbol, quote_cur.symbol))
                    # Missing IndexPair, create new one
                    ip = IndexPair(
                        quote_currency_id=quote_cur.id,
                        base_currency_id=base_cur.id,
                        quote_symbol=quote_cur.symbol,
                        base_symbol=base_cur.symbol,
                        active=True,
                        candle_1h=True
                    )
                    db_session.add(ip)
                    db_session.commit()

    except Exception as e:
        log.error(e)