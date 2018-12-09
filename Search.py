import json
import requests

import nltk.stem.porter as stemmer
from flask import Flask
from flask import request

from analyzer import normalize


app = Flask(__name__)

'''
Main search service
'''
@app.route("/search", methods=["POST"])
def search():
    json_data = request.json
    query = json_data['query']
    category = json_data['category']
    print(json_data)
    
    if query is None:
        response_reverceindex = requests.post('http://127.0.0.1:13538/reverseindex', 
                                          json={'data': None,
                                                'category': category,
                                                'max_docs':json_data.get('max_docs', 10)})
        parsed_reverceindex = json.loads(response_reverceindex.text)
        
        response_docs_snippets = requests.post('http://127.0.0.1:13542/snippets', 
                                           json={'data': parsed_reverceindex['processed_data'],
                                                'position': parsed_reverceindex['position']})
        parsed_docs_snippets = json.loads(response_docs_snippets.text)
        result = json.dumps({"status":"ok", "documents": parsed_docs_snippets['processed_data']}, 
                      ensure_ascii=False)
    else:
    
        processed_query = normalize(query)

        '''# call Analysis service to process query
        response_analyze = requests.post('http://127.0.0.1:13533/analyze', json={'data' : query})
        parsed_analyze = json.loads(response_analyze.text)'''

        # call ReverseIndex service to create reverse index
        response_reverceindex = requests.post('http://127.0.0.1:13538/reverseindex', 
                                              json={'data': processed_query,
                                                    'category': category,
                                                    'max_docs':json_data.get('max_docs', 10)})
        parsed_reverceindex = json.loads(response_reverceindex.text)

        # call Snippets service to create snippet for each document
        response_docs_snippets = requests.post('http://127.0.0.1:13542/snippets', 
                                               json={'data': parsed_reverceindex['processed_data'],
                                                    'position': parsed_reverceindex['position']})
        parsed_docs_snippets = json.loads(response_docs_snippets.text)

        result = json.dumps({"status":"ok", "documents": parsed_docs_snippets['processed_data']}, 
                          ensure_ascii=False)
        
    return result

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13565)