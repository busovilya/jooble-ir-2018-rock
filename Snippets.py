import json
import string
import requests

from flask import Flask, request
from nltk.tokenize import sent_tokenize

app = Flask(__name__)

'''
This service makes snippets for documentss
'''
@app.route('/snippets', methods =['POST'])
def snippets():
    json_data = request.json
    docs = json_data['data']
    # index of sentences in which there are words from query
    position = json_data['position']
 
    # snippet for every doc is the first sentence \
    # where you can find the word from the query
    for doc in docs:
        sentences = sent_tokenize(doc['text'])  
      
        pos = position[str(doc['id'])]
        pos.sort()
        
        if len(pos) != 0:
            doc['snippet'] = sentences[pos[0]]
        else:
            # if we can't find the word in text (it can be in title)
            doc['snippet'] = sentences[0]
        del doc['text']
    
           
    return json.dumps({'status':'ok', 'got_data': docs, 'processed_data':docs}, ensure_ascii=False)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13542)