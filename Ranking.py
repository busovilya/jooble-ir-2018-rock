import json
import configparser

import numpy as np
from flask import Flask, request

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')
'''
Service for ranking.
Input - list with relevant docIDS, list with tokens 
from the query.
Output - list with ranked docIDs.    

Cosine between normalized tf_idf vector of query 
and normilized tf_idf vector of document is used for ranking.

Before using this service for ranking you must create idf and
normalized tf_idf from inverted index by using ReverseIndex Service.
'''

@app.route('/rank', methods =['POST'])
def ranking():
    j = request.json
    # list with relevant docID:
    documents = j['documents']
    # list with tokens from the query:
    words = j['words']
    
    cos = {key: 0 for key in documents}    
    if words is None:
        
        for docID in documents:
            cos[docID] = sum(tf_idf[str(docID)].values())
    else:    
        # dictionary with tf_idf for query:
        tf_idf_query = {term: idf[term] / len(set(words)) for term in words}
        # normalization:
        norm = (sum([i ** 2 for i in tf_idf_query.values()])) **.5
        tf_idf_query = {term: tf_idf_query[term] / norm for term in words}
        
        for docID in documents:
            print(docID)
            cos[docID] = sum([tf_idf_query[term] * tf_idf[str(docID)][term] 
                              for term in words])
    
    # sorting documents
    ranked = sorted(cos.items(), key=lambda kv: kv[1], reverse = True)
    ranked = [d[0] for d in ranked]
      
    return json.dumps({'status':'ok', 'ranked': ranked})


@app.route("/rank/idf", methods=['POST'])
def refresh_idf():
    '''
    
    idf = {term: idf}
    
    normalized tf_idf = {
        docID1: {term1: tf_idf_docID1_term1, term2: tf_idf_docID1_term2, ...},
        docID2: {term1: tf_idf_docID2_term1, term3: tf_idf_docID2_term3, ...}, 
        ...,
        docIDn: {...}
        }   
    '''
    global idf
    global tf_idf
    
    j = request.json
    idf = j['idf']
    tf_idf = j['tf_idf']
    return json.dumps({'status':'ok'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config['Ranking']['Port'])