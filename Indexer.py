import gzip
import json
import os
import time
import pickle
import requests
import configparser
from collections import Counter

from json import JSONDecodeError
from flask import Flask
from flask import request
import pandas as pd
import numpy as np

from Document import Document
from analyzer import normalize


def position_in_text(lst, term):
    '''
    lst - list of tokens
    term - term that you are looking for
    Return all positions of term in the list of tokens(0 = first token) 
    '''
    return [i for i, x in enumerate(lst) if x == term]

def position_in_sentences(lst, term):
    '''
    lst - list of list, where each nested list - seperate sentences
    term - term that you are looking for
    Return all sequence numbers of sentences in which you can find term (0 = first sentence) 
    '''    
    return [i for i, x in enumerate(lst) if term in x]


def idf(inverted_index):
    '''
    The function returns inverted document frequency
    for each term in inverted_index.
    
    Input: inverted_index - fresh inverted index.
    '''
    number_of_docs = docs.shape[0]
    idf = {term: np.log(number_of_docs / len(inverted_index[term])) for term in list(inverted_index.keys())}    
    return idf


def tf(document):
    '''
    The function returns tf for a certain document
    
    Input: dictionary that matches certain document
            and term (from inverted index)
    '''
    # len(document.position_text) - number of term appearances in the text
    # len(document.position_title) - number of term appearances in the title
    # w - weight for word in title
    w = 5
    return np.log(1 + (len(document.position_text) + w*len(document.position_title))
                  / document.doc_len)


def normalized_tf_idf_docs(inverted_index, docs, idf):
    '''
    The function creates dictionary for every document 
    with normalized tf_idf for terms that appear in this document.
    
    Input: dictionary with idf for every term; DataFrame with document;
            inverted index.
    Output: {
            docID1: {term1: tf_idf_docID1_term1, term2: tf_idf_docID1_term2, ...},
            docID2: {term1: tf_idf_docID2_term1, term3: tf_idf_docID2_term3, ...}, 
            ...,
            docIDn: {...}
            }
    '''
    tf_idf = {int(docID): {} for docID in docs.id.unique()}    
    
    for term in inverted_index.keys():
        for document in inverted_index[term]:
            tf_idf[document.id][term] = tf(document) * idf[term]
            
    # normalization:
    for docID in tf_idf.keys():
        norm = sum([i**2 for i in tf_idf[docID].values()])**.5
        tf_idf[docID] = {i[0]: i[1] / norm for i in tf_idf[docID].items()}
        
    return tf_idf


def intersect_all(terms, inverted_index):
    '''
    terms - list of terms for wich we want to intersect set of documents
    inverted_index - created inverted index
    '''
            
    if terms == []:
        return set()
    
    ans = set()
    for term in terms:            
        p = inverted_index.get(term)
        posting_list = set()
        for d in p:
            posting_list.add(d.id)
        if len(ans) == 0:
            ans = posting_list
        else:
            ans = ans & posting_list
    
    # if posting lists for terms don't intersect
    if ans == set():
        # find doc frequency because we want to find the rarest (more informational) term 
        # df -> {doc_freq: term}
        df = {len(inverted_index.get(term)): term for term in terms}
        term_with_min_df = df[min(list(df.keys()))]
        p = inverted_index.get(term_with_min_df)
        for d in p:
            ans.add(d.id)
    
    return ans


def add_to_revesed_index(row):
    global inverted_index
    doc = dict()
    doc['docID'] = int(row['id'])
        
    doc['text_searchable'] = normalize(row['text'])
    doc['title_searchable'] = normalize(row['title'])
        
    tokens_text = doc['text_searchable']
    tokens_title = doc['title_searchable']

    tokens_text_flat = [item for sublist in tokens_text for item in sublist]
    tokens_title_flat = [item for sublist in tokens_title for item in sublist]
                
    number_of_occurrences = Counter(tokens_text_flat + tokens_title_flat)         
    for term in set(tokens_text_flat + tokens_title_flat):
        if term not in inverted_index:            
            inverted_index[term] = [Document(doc['docID'],
                                                  number_of_occurrences[term],
                                                  term,
                                                  tokens_text,
                                                  tokens_title)] 
        else:
            inverted_index[term].append(Document(doc['docID'],
                                                     number_of_occurrences[term],
                                                     term,
                                                     tokens_text,
                                                     tokens_title))


inverted_index = dict()
read_files = set()
docs = pd.DataFrame()

config = configparser.ConfigParser()
config.read('config.ini')


app = Flask(__name__)

@app.route("/reverseindex", methods=["POST"])
def reverseindex():
    global docs
    global inverted_index
    json_data = request.json
    words = json_data['data']
    category = json_data['category']
    documents = list()
    
    if words is None and category:
        documents = docs.loc[docs['profarea'] == category, 'id'].tolist()
    else:    
        # create flat list from list of lists
        words = [item for sublist in words for item in sublist]

        # reject words that are not in the inverted index
        words = [term for term in words if inverted_index.get(term) is not None]

        # intersect lists of documents for all processed words in query
        documents = list(intersect_all(words, inverted_index))
        
        if category:
            category_id = docs.loc[docs['profarea'] == category, 'id'].tolist()
            documents = [docID for docID in documents if docID in category_id]

    # ranking if len(documents) is more than one
    if len(documents) > 1:
        response_ranked = requests.post(f"http://127.0.0.1:{config['Ranking']['Port']}/rank",
                                        json={'documents': documents,
                                              'words': words})
        parsed_ranked = json.loads(response_ranked.text)
        documents = parsed_ranked['ranked']
    
    # if maximal numbers of documents given, then select only the desired amount
    if json_data.get('max_docs'):
        documents = documents[:json_data.get('max_docs')]        
    
    # need this because type(docs['id']) is string in this dataFrame
    documents = [x for x in documents]
            
    # index of sentences(first/second/etc) in which there are words from query for every doc
    pos = {key: [] for key in documents}
    if words is not None:
        for term in words:        
            p = inverted_index.get(term)
            for docID in documents:
                for d in p:
                    if d.id == int(docID):
                        pos[docID] += d.position_sentence
                          
    # get text of found documentss
    ranked_documents = []
    for document in documents:
        ranked_documents += docs.loc[docs['id'] == int(document),
                                     ['id', 'title', 'text', 'url', 'profarea']].to_dict('records')
      
    return json.dumps({"status":"ok", "got_data":json_data['data'], 
                       "processed_data": ranked_documents, "position": pos})


@app.route("/reverseindex/add", methods=['POST'])
def add():
    global docs
    global inverted_index
        
    docs_new = pd.read_csv(config['Data']['Path'] + 'documents.csv', sep='\t')
    docs_new = docs_new.iloc[:100,:]

    docs_new.apply(lambda row: add_to_revesed_index(row), axis=1)                
            
    docs = docs.append(docs_new)
    # refresh idf and sent into service for ranking  
      
    #create idf and normilized tf_idf from saved inverted_index
    dict_idf = idf(inverted_index)
    dict_tf_idf = normalized_tf_idf_docs(inverted_index, docs, dict_idf)    
    requests.post(f"http://127.0.0.1:{config['Ranking']['Port']}/rank/idf", json={'idf' : dict_idf,
                                                           'tf_idf': dict_tf_idf})


    return json.dumps({"status":"ok"}, ensure_ascii=False)

        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config['Indexer']['Port'])