class Document:
    def __init__(self, id, count, term, text_tokens, title_tokens):
        self.id = id
        self.count = count
        self.position_text = self.position_in_doc(text_tokens, term)
        self.position_title = self.position_in_title(title_tokens, term)
        self.title_flag = any(term in sent for sent in title_tokens)
        self.position_sentence = self.position_in_sentence(text_tokens, term)
        self.doc_len = self.get_doc_len(text_tokens, title_tokens)

    def get_doc_len(self, text_tokens, title_tokens):
        length = 0
        
        for sent in text_tokens:
            length += len(sent)
            
        for sent in title_tokens:
            length += len(sent)
            
        return length
        
    def position_in_doc(self, text_tokens, term):
        flat_list_of_text_tokens = [item for sublist in text_tokens for item in sublist]
        return [i for i, x in enumerate(flat_list_of_text_tokens) if x == term]

    def position_in_title(self, title_tokens, term):
        flat_list_of_title_tokens = [item for sublist in title_tokens for item in sublist]
        return [i for i, x in enumerate(flat_list_of_title_tokens) if x == term]

    def position_in_sentence(self, text_tokens, term):
        return [i for i, x in enumerate(text_tokens) if term in x]