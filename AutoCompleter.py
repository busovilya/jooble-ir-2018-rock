import pickle
import json

from flask import Flask
from flask import request
from flask_cors import CORS
from flask import jsonify



alpabet = 'abcdefghijklmnopqrstuvwxyz абвгдеёжзийклмнопрстуфхцчшщъыьэюяє0123456789+#-'

class TrieNode:
    def __init__(self, key='', value=False):
        self.key = key
        self.value = value
        self.child = dict()
        for char in alpabet:
            self.child[char] = None

    def __repr__(self):
        return self.key

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, key):
        node = self.root
        for char in key:
            if node.child[char] is None:
                node.child[char] = TrieNode(char)
            node = node.child[char]
        node.value = True

    def search(self, key):
        node = self.root
        for char in key:
            if node.child[char] is None:
                return False
            node = node.child[char]
        return node

    
    def dfs(self, node):
        visited = set()
        stack = [(node, [])]
        while stack:
            (cur_node, path) = stack.pop()
            if cur_node not in visited:
                visited.add(cur_node)
                if cur_node.value:
                    yield path+[cur_node]
                for child in cur_node.child.values():
                    if child is not None:
                        stack.append((child, path + [cur_node]))

    def autocomplete(self, word):
        for el in list(self.dfs(self.search(word))):
            yield word + ''.join(list(map(lambda x:x.key, el)))[1:]

    
    def get_hints(self, word):
        result = dict()
        for word in list(self.autocomplete(word)):
            result[word] = words[word]

        return sorted(result, key=result.get, reverse=True)


words = []

with open('../title_words.pickle', 'rb') as file:
    words = pickle.load(file)

trie = Trie()
for index, word in enumerate(words.keys()):
    trie.insert(word)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    word = request.json['query']
    hints = trie.get_hints(word)
    response = jsonify(hints)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=13561)