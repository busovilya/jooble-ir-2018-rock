import json
import requests
import configparser

import nltk.stem.porter as stemmer
from flask import Flask
from flask import request

from analyzer import normalize


app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

'''
Main search service
'''
@app.route("/search", methods=["POST"])
def search():
    json_data = request.json
    query = json_data['query']
    category = json_data['category']

    processed_query = normalize(query)

    # call ReverseIndex service to create reverse index
    response_reverceindex = requests.post(f"http://127.0.0.1:{config['Indexer']['Port']}/reverseindex", 
                                              json={'data': processed_query,
                                                    'category': category,
                                                    'max_docs':json_data.get('max_docs', 10)})
    parsed_reverceindex = json.loads(response_reverceindex.text)
    
    response_docs_snippets = requests.post(f"http://127.0.0.1:{config['Snippets']['Port']}/snippets", 
                                           json={'data': parsed_reverceindex['processed_data'],
                                                'position': parsed_reverceindex['position']})
    parsed_docs_snippets = json.loads(response_docs_snippets.text)

    return json.dumps({"status":"ok", "documents": parsed_docs_snippets['processed_data']}, 
                      ensure_ascii=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config['Search']['Port'])