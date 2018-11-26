class Document:
    '''
    text_tokens - list of lists
    title_tokens - list of lists
    '''
    def __init__(self, id, text_tokens, title_tokens):
        self.id = id
        self.title_tokens = title_tokens
        self.text_tokens = text_tokens

    def position_in_doc(self, term):
    '''
    term - term that you are looking for
    Return all positions of term in the list of text tokens(0 = first token)
    '''
        flat_list_of_text_tokens = [item for sublist in self.text_tokens for item in sublist]
        return [i for i, x in enumerate(flat_list_of_text_tokens) if x == term]

    def position_in_title(self, term):
    '''
    term - term that you are looking for
    Return all positions of term in the list of title tokens(0 = first token) 
    '''
        flat_list_of_title_tokens = [item for sublist in self.title_tokens for item in sublist]
        return [i for i, x in enumerate(flat_list_of_title_tokens) if x == term]

    def position_in_sentence(self, term):
        '''
        lst - list of list, where each nested list - seperate sentences
        term - term that you are looking for
        Return all sequence numbers of sentences in which you can find term (0 = first sentence) 
        '''    
        return [i for i, x in enumerate(self.text_tokens) if term in x]