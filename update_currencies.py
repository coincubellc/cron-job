import requests
from database import *


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

CMC_API_KEY = os.getenv('CMC_API_KEY')
CMC_LIMIT = os.getenv('CMC_LIMIT')

_base_url = 'https://pro-api.coinmarketcap.com'
headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}


def get_coins():
    # Get market data from CMC
    log.info("Getting tickers from CoinMarketCap...")
    url = _base_url + '/v1/cryptocurrency/listings/latest?start=1&limit=' + CMC_LIMIT
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        coins = resp.json()['data']
        coins.append({'symbol': 'USD', 'name': 'US Dollar'})
        coins.append({'symbol': 'EUR', 'name': 'Euro'})
        coins.append({'symbol': 'GPB', 'name': 'British Pound'})
        return coins
    else:
        return []

def add_coins(coins):
    for coin in coins:
        symbol = coin['symbol']
        # Catch and replace inconsistencies between coinmarketcap and ccxt
        if symbol == 'MIOTA':
            symbol = 'IOTA'
        log.debug(f"Checking: {symbol}")
        cur = Currency.query.filter_by(symbol=symbol).first()

        if not cur:
            try:
                log.debug(f"Adding asset: {symbol}")
                asset = Currency(
                    symbol=symbol,
                    name=coin['name'],
                    market_cap=coin['quote']['USD']['market_cap'],
                    cmc_id=coin['slug']
                    )
                db_session.add(asset)
            except:
                asset = Currency(
                    symbol=symbol,
                    name=coin['name']
                    )
                db_session.add(asset)

    db_session.commit()

def update_currencies(coins):
    log.info("Updating all currencies...")
    # Loop through coins and update currencies
    for coin in coins:
        symbol = coin['symbol']
        if symbol == 'MIOTA':
            symbol = 'IOTA'
        cur = Currency.query.filter_by(symbol=symbol).first()
        log.info(f"Updating {cur}")
        log.info(coin)
        volume_24h = round(float(coin['quote']['USD']['volume_24h']))
        log.info(volume_24h)
        if cur:
            try:
                cur.num_market_pairs = coin['num_market_pairs']
                cur.circulating_supply = coin['circulating_supply']
                cur.total_supply = coin['total_supply']
                cur.max_supply = coin['max_supply']
                cur.price = coin['quote']['USD']['price']
                cur.volume_24h = volume_24h
            except KeyError:
                pass
            try:
                cur.percent_change_1h = float(coin['quote']['USD']['percent_change_1h'])
            except KeyError:
                cur.percent_change_1h = 0
            try:
                cur.percent_change_24h = float(coin['quote']['USD']['percent_change_24h'])
            except KeyError:
                cur.percent_change_24h = 0
            try:
                cur.percent_change_7d = float(coin['quote']['USD']['percent_change_7d'])
            except KeyError:
                cur.percent_change_7d = 0
            try:
                cur.market_cap = coin['quote']['USD']['market_cap']
            except KeyError:
                cur.market_cap = 0
            cur.save_to_db()
        else:
            log.info(f'Missing asset: {symbol}')
            pass
    db_session.commit()

def update_index_assets(coins):
    # Rank dictionary
    ranks = {}
    usd_removed = 0
    for coin in coins:
        symbol = coin['symbol']
        if symbol == 'MIOTA':
            symbol = 'IOTA'
        if symbol in ['USDT', 'TUSD', 'USDC', 'USDS', 'GUSD', 'PAX']:
            usd_removed += 1
            continue
        if not usd_removed:
            ranks[coin['cmc_rank']] = symbol
        else:
            ranks[coin['cmc_rank'] - usd_removed] = symbol

    # Update index assets by rank
    indices = Indices.query.all()
    for index in indices:
        index_count = index.count
        log.info(f"Updating {index.type} index assets by rank...")
        index_curs = []
        for rank in ranks.keys():
            if rank <= index_count:
                cur = Currency.query.filter_by(symbol=ranks[rank]).first()
                if cur:
                    index_curs.append(cur)
        log.info(index.type)
        log.info(index_curs)
        index.currencies = index_curs
        db_session.add(index)
    db_session.commit()
    log.info("Updated all indices by rank.")

def update_all_currencies():
    try:
        coins = get_coins()
        add_coins(coins)
        update_currencies(coins)
        update_index_assets(coins)
    except Exception as e:
        log.error(e)

if __name__ == '__main__':
    update_all_currencies()