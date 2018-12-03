Run all services mentioned above and open UI client to do search. 
Link to view diagram: http://afly.co/2ds

# Search service : main manager for all workflow.
Port: port 13565

Input paramets: 
- query - query from user
- max_docs - maximum number of documents returned by the search engine  

Actions:
1. request to service Analyze -> receive json with key "words"- prepared query (list of terms).
2. request to service ReverseIndex -> receive json with key "processed_data" - dictionary with docID's and texts.
3. request to service Snippets -> receive json with key "processed_data" - dictionary with docID's and snippets.  

Return: 
- documents - dictionary with docID's and snippets.

# Analyze service : manager for services that execute text processing. 
Port: 13533

Input:
- data - unprepared query from user or unprepared text from documents.

Actions:  
  1. request to service Tokenizing -> receive json with key "processed_data" - list of tokens.
  2. request to service Stemmer -> receive json with key "processed_data" - list of terms.

Return:
- words - list of terms.

# Tokenizing service : tokenizer for recieved query or text.
Port: 13549

Input: 
- data - query or text in string format. 
It uses word_tokenize from nltk.tokenize.

Return:
- processed_data - list of lists of tokens.

# StopWords service : drops stop words.
Port: 13536

Input: 
- data - list of lists of tokens. 
It uses stopwords from nltk.corpus.

Return:
- processed_data - list of lists tokens.

# Stemming service : stemmer for recieved list of tokens.
Port: 13535

Input: 
- data - list of lists of tokens. 

It uses nltk.stem.porter.

Return:
- processed_data - list of lists of term.

# Service ReverseIndex : executes search by term in inverted index.
Port: 13538

Input: 
 - data - list of terms
 - max_docs - maximum number of documents returned by the search engine. 

Actions:  
  1. You can find function create_inverted_index() for creating inverted index from "eval_texts.csv" in ReverseIndex.ipynb. 
  Execute the function before starting to work with a search engine.

Return: processed_data - dictionary with docID's and texts (number of docID == max_docs). {'id': docID, 'text': text}

# Snippets service : creates snippet - first sentence which contains any term from query.
Port: 13542

Input: 
- data - dictionary with docID's and texts (number of docID == max_docs).

Return: processed_data - dictionary with docID's and snippets. {'id': docID, 'snippet': snippet}

# Service Client_UI : creates UI for receiving user queries and displaying search results.
Port: 13560

You can change 'max_docs' here.
Actions: 
  1. request to service SpellChecker -> recieve json with key "state" - equal 1 if mistakes were found else 0, 
  "processed_data" - correct query.
  2. request to service Search -> recieve json with key "documents" - dictionary with docID's and snippets.
  
# Service SpellChecker : checks query for mistakes and returns correct query if any were found.
Port: 13539

You need to create class object with language model which can be obtained from "Data/list_of_words.pickle"

Input: 
- query - query from user. 

Actions: 
  1. request to service Tokenizing ->  receive json with key "processed_data" - list of tokens.
  
Return:
- processed_data - correct query (type str)
- state - equal 1 if mistakes were found else 0.
