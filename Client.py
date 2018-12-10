import requests
import json
import configparser

from flask import Flask, render_template
from flask import request

from spellchecker import QueryChecker

spell_cheker = QueryChecker()
config = configparser.ConfigParser()
config.read('config.ini')

def rendering(query = None, category = None):
    print('rendering:',query, category)
    if query is not None:
        print('query isnt none')
        checker = spell_cheker.check(query)

        if checker['state']:
            # if checker found mistakes in the query
            r = requests.post(f"http://127.0.0.1:{config['Search']['Port']}/search", 
                              json={'query': checker["query"], 
                                    'category': category,
                                    'max_docs': 10}).json()["documents"]
            if len(r) == 0:
                return render_template('blank.html', old_query=query)
            snippet = [doc['snippet'] +' (' + str(doc['id']) +')' for doc in r]
            print(snippet)

            return render_template('checked.html', old_query=query,
                                   checked_query=checker["query"],
                                   documents=r)
        else:
            r = requests.post(f"http://127.0.0.1:{config['Search']['Port']}/search", 
                              json={'query': query, 'category': category, 
                                    'max_docs': 10}).json()["documents"]
            if len(r) == 0:
                return render_template('blank.html', old_query=query)
            snippet = [doc['snippet'] +' (' + str(doc['id']) +')' for doc in r]
            print(snippet)

            return render_template('result.html', old_query=query, 
                                   query=query,documents=r, 
                                   snippet=snippet)
        
    else:
        print('query is none')
        r = requests.post(f"http://127.0.0.1:{config['Search']['Port']}/search", 
                              json={'query': None, 'category': category,
                                    'max_docs': 10}).json()["documents"]
        

        snippet = [doc['snippet'] +' (' + str(doc['id']) +')' for doc in r]

        return render_template('result.html', old_query=query,
                               documents=r, snippet=snippet)


app = Flask(__name__)
  

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    
    formData = request.values if request.method == "POST" else request.values
    query = formData['query']
    category = formData['category']   
    
    if not query and category == 'none':
        return render_template('blank.html', old_query=query)
    else:
        if query and category == 'none':
            result = rendering(query=query)        
        if not query and category != 'none':
            result = rendering(category=category)
        if query and category != 'none':
            result = rendering(query=query, category=category)    
    
    return result

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=13560)