from flask import Flask
from flask import jsonify
from flask import request
import pymorphy2
from gensim.models import KeyedVectors
import pickle
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)

model_w2v_ru = KeyedVectors.load_word2vec_format('../web_0_300_20.bin', binary=True)
model_ru = pymorphy2.MorphAnalyzer()
with open('../title_words.pickle', 'rb') as file:
    title_words = pickle.load(file)

@app.route('/similar', methods=['POST'])
def similar():
    word = request.json['query']
    word_pos = model_ru.parse(word)[0].tag.POS
    similar_words = model_w2v_ru.most_similar(word+'_'+word_pos)
    words = list(map(lambda x:x[0].split('_')[0], similar_words))

    words_in_title = []
    for word in words:
        if word in title_words.keys():
            words_in_title.append(word)
    
    response = jsonify(words_in_title)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__=='__main__':
    app.run(host='127.0.0.1', port=13562)