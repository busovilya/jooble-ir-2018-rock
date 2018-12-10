Run all services mentioned above and open UI client to do search. 

# Search service : main manager for all workflow.
Port: port 13565

Input paramets: 
- query - query from user
- max_docs - maximum number of documents returned by the search engine  

Actions:
1. import analyzer -> create prepared query (list of terms).
2. request to service ReverseIndex -> receive json with key "processed_data" - dictionary with docID's and texts.
3. request to service Snippets -> receive json with key "processed_data" - dictionary with docID's and snippets.  

Return: 
- documents - dictionary with docID's and snippets.

# Service Indexer : executes search by term in inverted index.
Port: 13538

Input: 
 - data - list of terms
 - max_docs - maximum number of documents returned by the search engine. 

Actions:  
  1. You need to create inverted_index from documents, idf and normilized_tf_idf before starting to work with a search engine.
  2. request to service Ranking -> receive json with key "ranked" - list with ranked docIDs.

Return: processed_data - dictionary with docID's and texts (number of docID == max_docs). {'id': docID, 'text': text}

# Service Ranking : executes ranking by using cosine between two vectors.
Port: 13541

Before using this service for ranking you must create idf and normalized tf_idf from inverted index by using ReverseIndex Service.

Input: 
 - documents - list with relevant docID
 - words - list with tokens from the query. 

Return: ranked - list with ranked docIDs

# Snippets service : creates snippet - first sentence which contains any term from query.
Port: 13542

Input: 
- data - dictionary with docID's and texts (number of docID == max_docs).

Return: processed_data - dictionary with docID's and snippets. {'id': docID, 'snippet': snippet}

# Service Client : creates UI for receiving user queries and displaying search results.
Port: 13560

You can change 'max_docs' here.
Actions: 
  1. import SpellChecker -> checks query for mistakes and returns correct query if any were found.
  2. request to service Search -> recieve json with key "documents" - dictionary with docID's and snippets.
  
