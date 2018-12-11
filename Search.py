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

category_query = {"Банки, инвестиции, лизинг":'банк',
"Юристы":'юрист', "Информационные технологии, интернет, телеком":"программист",
"Наука, образование":'учитель', "Производство":"производство", 
"Туризм, гостиницы, рестораны":["туризм","повар","официант"], 
"Бухгалтерия, управленческий учет, финансы предприятия":"бухгалтер",
"Начало карьеры, студенты":"студент", "Управление персоналом, тренинги":"менеджер",
"Продажи":"продавец", "Транспорт, логистика":"водитель", "Медицина, фармацевтика":"врач",
"Высший менеджмент":"директор", "Маркетинг, реклама, PR":["seo","маркетолог"],
"Автомобильный бизнес":"механик", "Закупки":"закупки", 
"Строительство, недвижимость":["архитектор","строитель"], "Рабочий персонал":"рабочий",
"Административный персонал":"директор", "Инсталляция и сервис":"сервис",
"Безопасность":"охранник", "Искусство, развлечения, масс-медиа":"дизайнер",
"Консультирование":"консультант", "Страхование":"страхование", "Домашний персонал":"няня",
"Добыча сырья":"шахтер"}

'''
Main search service
'''
@app.route("/search", methods=["POST"])
def search():
    json_data = request.json
    query = json_data['query']
    category = json_data['category']

    if query is None and category:
        query = category_query[category]

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