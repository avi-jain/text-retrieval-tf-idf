#######################################################################
# QUERY MODULE
#######################################################################

# This is the query processing module of our project.
# Module will pre and post process the query for analysis
# As of now, this module provides the interface ->

# FUNCTIONS -
# query(str) - This function recieves the input that was taken from the
#              user, as a string. It calls the relevant internal functions
#              to tokenize and normalize the query, then perform a vector-
#              space comparision with the document database, to find out
#              relevant documents and rank them accordingly. This function
#              then returns a list of the top 20 most relevant documents

#######################################################################
# External libraries we'll be using
#######################################################################

import nltk

from collections import Counter

#######################################################################
# Modules of our project that we'd be using
#######################################################################

import global_vars

#######################################################################
# Functions
#######################################################################

# NOTE :-
# I have temporarily removed the detection of synonyms.
# Pliz, add that into this.

# NOTE :-
# This function computes SQUARE of the cosine
# This is a different value, but shouldn't change the ordering
# This is because sqrt is expensive


def query(string):
    # Tokenize the query and remove puncutation
    query_tokenized = nltk.tokenize.casual_tokenize(string.lower())

    query_tokenized = [w for w in query_tokenized if len(w) > 1
                       or w[0].isalnum()]

    # Lemmatize the tokens
    lem = nltk.stem.WordNetLemmatizer()
    query_lm = []
    for w in query_tokenized:
        query_lm.append(lem.lemmatize(lem.lemmatize(w), 'v'))

    # Create a dictionary mapping unique tokens to thei frequency
    tok_counts = Counter(query_lm)
    # N = number of unique tokens
    N = len(tok_counts.keys())
    for term in tok_counts.keys():
        tok_counts[term] /= N

    # For easier reference to the DocDB object
    docdb_obj = global_vars._DOC_DB_OBJ

    # Initialize all scores and magnitutes to 0
    doc_scores = [0 for i in range(len(docdb_obj.id_list))]

    # For every unique term in the query, iterate over documents which have
    # the term and add their score to the appropriate index of the list
    for term in tok_counts.keys():
        if term in docdb_obj.tf.keys():
            for (doc_num, tf) in docdb_obj.tf[term]:
                doc_scores[doc_num] += tok_counts[term] \
                                       * docdb_obj.idf[term] * tf
        else:
            l = len(term)
            for _term in docdb_obj.tf.keys():
                if _term.startswith(term):
                    for (_doc_num, _tf) in docdb_obj.tf[_term]:
                        doc_scores[_doc_num] += tok_counts[term] \
                                                * docdb_obj.idf[_term] \
                                                * _tf * (l / len(_term))

    # Ranking of results is independent of query magnitude, so we won't
    # calculate that

    # Make a list of tuples of docname and score
    doc_list = [(docdb_obj.id_list[i][1], doc_scores[i])
                for i in range(len(doc_scores)) if doc_scores[i] > 0]

    # Sort and reverse
    doc_list.sort(key=lambda x: x[1])
    doc_list.reverse()

    # And return the list
    return doc_list
