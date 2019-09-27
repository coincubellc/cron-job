from database import (Algorithm, Exchange, Indices, Role)

EXCHANGES = [
    {'name': 'Binance', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': None},
    {'name': 'Bitstamp', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': 'Customer ID'},
    {'name': 'Bittrex', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': None},
    {'name': 'CoinbasePro', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': 'Passphrase'},
    {'name': 'Coss', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': None},
    {'name': 'Kucoin', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': 'API Password'},
    {'name': 'Liquid', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': None},
    {'name': 'Poloniex', 'key': 'API Key', 'secret': 'API Secret', 'passphrase': None},
]
ROLES = ['Admin', 'User']
ALGORITHMS = [{'name': 'Centaur', 'description': 'Customizable portfolio allocation and rebalancing algorithm'}]
INDICES = [
    ('top_five', 5),
    ('top_ten', 10),
    ('top_twenty', 20),
    ('top_thirty', 30),
    ('top_forty', 40),
    ('top_fifty', 50),
    ('top_hundred', 100)
]

def seed_db():

    for ex in EXCHANGES:
        if not Exchange.query.filter_by(name=ex['name']).first():
            exchange = Exchange(
                name=ex['name'],
                key=ex['key'],
                secret=ex['secret'],
                passphrase=ex['passphrase'],
                active=True
            )
            exchange.save_to_db()


    for role in ROLES:
        if not Role.query.filter_by(name=role).first():
            nr = Role(
                name=role
            )
            nr.save_to_db()


    for algo in ALGORITHMS:
        if not Algorithm.query.filter_by(name=algo['name']).first():
            algorithm = Algorithm(
                name=algo['name'],
                description=algo['description'],
                active=True
            )
            algorithm.save_to_db()

    for index in INDICES:
        if not Indices.query.filter_by(type=index[0]).first():
            ind = Indices(
                type=index[0],
                count=index[1]
            )
            ind.save_to_db()