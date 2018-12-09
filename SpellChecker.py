import re
import json
import os
import requests
import pickle
import configparser
from collections import Counter

from flask import Flask
from flask import request

from analyzer import tokenizer

class SpellChecker:
    def __init__(self, model):
        self.model = model    
        self.WORDS = self.words()
                
    def words(self):
        return set(self.model.keys())
    
    def P(self, word): 
        return self.model.get(word, 0)

    def correction(self, word): 
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.P)
    
    def correct(self, words):
        for word in words:
            if len(word) > 10 and word not in self.WORDS:
                return self.segment(word)
        return [self.correction(word) for word in words]

    def candidates(self, word): 
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edits1(word)) or 
                    self.known(self.edits2(word)) or [word])

    def known(self, words): 
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(words) & self.WORDS


    def edits1(self, word):
        "All edits that are one edit away from `word`."
        #letters    = 'abcdefghijklmnopqrstuvwxyz'
        letters = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        self.edits_1 = list(set(deletes + transposes + replaces + inserts))
        return set(deletes + transposes + replaces + inserts)
      
    def edit(self, word):
        "All edits that are one edit away from `word`."
        #letters    = 'abcdefghijklmnopqrstuvwxyz'
        letters = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)
        

    def edits2(self, word): 
        "All edits that are two edits away from `word`."
        answer = self.edit(list(self.edits_1)[0])
        for w in list(self.edits_1)[1:]:
            answer |= self.edit(w)
        return answer   
    
    def Pwords(self, words):
        "Probability of words, assuming each word is independent of others."
        return self.product(self.model.get(w,1e-9) for w in words)

    def product(self, nums):
        "Multiply the numbers together.  (Like `sum`, but with multiplication.)"
        result = 1
        for x in nums:
            result *= x
        return result
    
    def splits(self, text, start=0, L=20):
        "Return a list of all (first, rest) pairs; start <= len(first) <= L."
        return [(text[:i], text[i:]) 
                for i in range(start, min(len(text), L)+1)]

    def segment(self, text):
        "Return a list of words that is the most probable segmentation of text."
        if not text: 
            return []
        else:
            candidates = ([first] + self.segment(rest) 
                          for (first, rest) in self.splits(text, 1))
            return max(candidates, key=self.Pwords)        
        
 
 # create model for spell checking
'''
config = configparser.ConfigParser()
config.read('config.ini')

path = config['Data']['Path']
'''

all_words = list()  
for root, dirs, files in os.walk("../Data"):  
    for filename in files:
        if 'list_of_words' in filename:
            with open('../Data/' + filename, 'rb') as file:
                try: 
                    all_words += pickle.load(file)
                except JSONDecodeError:
                    print("Can't read file " + filename)
    
probability_dist = Counter(all_words)
N = sum(probability_dist.values())
for key in probability_dist:
    probability_dist[key] /= N
    
sc = SpellChecker(probability_dist)

app = Flask(__name__)

@app.route("/spellchecker", methods=["POST"])
def checking():
    json_data = request.json
    query = json_data['query']
        
    # tokenizing (create list of lists where each list is separate token)
    tokenized = tokenizer.tokenize(query) 
    
    # words - list of tokens from query
    words = [item for sublist in tokenized for item in sublist]
    # create list of correct words
    correct_words = sc.correct(words)
    
    state = 0
    correct_query = query
    for i in zip(words, correct_words):
        if i[0] != i[1]:
            state = 1
            correct_query = ' '.join(correct_words)
        
    return json.dumps({"status":"ok", "got_data":json_data['query'], 
                       "processed_data": correct_query, "state": state}, ensure_ascii=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13539)