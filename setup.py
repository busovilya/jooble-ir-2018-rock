import configparser

import Search
import Indexer

config = configparser.ConfigParser()
config.read('config.ini')

Search.app.run(host='0.0.0.0', port=config['Search']['Port'])
Indexer.app.run(host='0.0.0.0', port=config['Indexer']['Port'])