import json

class Document:
    def __init__(self, id):
        self.id = id

    
    def to_json(self):
        return json.dumps({'doc_id':self.id})