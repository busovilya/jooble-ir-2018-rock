import json
import re

import langdetect
from nltk.stem.snowball import SnowballStemmer
import nltk.tokenize
from nltk.corpus import stopwords

class LanguageDetector:
    def __init__(self):
        self.friendly = {'eng': 'english', 'rus': 'russian', 'deu':'german','fra': 'french', 'lad':'spanish',
                'por':'portuguese', 'ita':'italian','ell':'greek',
                'nob':'norwegian', 'dan':'danish','nld':'dutch', 'swe':'swedish',
                'en' : 'english', 'ru':'russian', 'de':'german', 'fr':'french', 'mk':'russian'}

    def detect(self, text):
        return self.friendly.get(langdetect.detect(text), 'english')    

class Stemmer:
    def __init__(self, lang):
        self.language = lang

    def stemWord(self, token):
        return SnowballStemmer(self.language).stem(token)

    def stemWords(self, tokens):
        return [self.stemWord(token) for token in tokens]


class Tokenizer:
    def __init__(self):
        self.regex = re.compile(r"[\w]+")

    def tokenize(self, text):
        # create list of string, where each string - separate sentence
        sentences = nltk.tokenize.sent_tokenize(text)  

        # tokens - list of lists, where each list - separate sentence
        tokens = [nltk.tokenize.word_tokenize(s.lower()) for s in sentences] 
        
        # remove punctuation and split term like '~salesman*-cashier' into ['salesman','cashier']
        tokens = [[item for sublist in
                [self.regex.findall(word) for word in sent]
                for item in sublist]
                for sent in tokens] 

        return tokens


class StopWords:
    def __init__(self, lang):
        self.language = lang
        self.heuristics = ['нужна', 'нужен', 'требуется', 'ищу', 'ищем', 
                  'работа', 'работу','приглашаем', 'тд', 'условия',
                 'требования']

    def dropStopWords(self, tokens):
        stop_words = set(stopwords.words(self.language) + self.heuristics)
        # create list of lists, where each nested list - separate sentence
        without_stop_words = [[w for w in lst if not w in stop_words] for lst in tokens]

        return without_stop_words

langDetector = LanguageDetector()
tokenizer = Tokenizer()

def normalize(query):
    languge = langDetector.detect(query)
    tokenized = tokenizer.tokenize(query)
    sw = StopWords(languge)
    stemmer = Stemmer(languge)
    without_stop_words = sw.dropStopWords(tokenized)
    stemmed = [stemmer.stemWords(sent) for sent in without_stop_words]
    return stemmed