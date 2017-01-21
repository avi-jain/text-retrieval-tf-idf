#######################################################################
# PREPROCESSOR MODULE
#######################################################################

# This module defines the preprocessing that the engine will perform on
# the documents in order to create the .pyirdocs.db file (the path to
# which will have been loaded to the global variable _DB_PATH.

# This module recommends the usage of only the following interface ->
#
# FUNCTIONS
#
# preprocess(of_obj) - This file takes in a file object for the .pyirdocs.db
#                      file as input and calls all relevant, required functions
#                      within the module to perform the required preprocessing
#                      on all documents in the directory (except the .db file
#                      itself. It then stores the result of the preprocessing
#                      in the .pyirdocs.db file, in the form of an object of
#                      the documents.DocDB class

#######################################################################
# Libraries we'll be using
#######################################################################

# We need this for listing files
import os
from os import path, listdir
from os.path import isfile, isdir

# We need this for tokenization and normalization
import nltk

# We need this for logarithms (calculating idf)
import math

# We need this for writing to the file as a binary file
import pickle

# We use this to group common tokens and get their frequency
from collections import Counter

#######################################################################
# Modules from our project that we'd be using
#######################################################################

# We need these global variables
import global_vars

# We need this for document-processing
import document

#######################################################################
# FUNCTIONS
#######################################################################


def _preprocess_file(docnum, docdb_obj, document):
    # Get absolute path to document
    doc_path = os.path.join(global_vars._DOCS_PATH, document)
    # Open the document in read mode
    if_obj = open(doc_path, "r")
    # Read the entire document
    text = if_obj.read()
    # Close the file object
    if_obj.close()
    # Tokenize the words in the document
    tokens = nltk.tokenize.casual_tokenize(text)
    # Remove all tokens which are individual puncutation elements
    tokens = [token for token in tokens if len(token) > 1 or
              token[0].isalnum()]
    # Lemmanite the tokens
    lemmatizer = nltk.stem.WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(lemmatizer.lemmatize(token.lower()), 'v')
              for token in tokens]
    # The total number of tokens in the document
    N = len(tokens)
    # A dictionary of all the unique tokens mapped to frequency
    tok_counts = Counter(tokens)
    # Loop over every unique token
    for term in tok_counts.keys():
        # If the term is not already present in the tf list of the object
        if term not in docdb_obj.tf.keys():
            # Set its tf for the particular document
            docdb_obj.tf[term] = [(docnum, tok_counts[term] / N)]
        # Else, if it does exist
        else:
            # Append tf to the existing list of tfs
            docdb_obj.tf[term].append((docnum, tok_counts[term] / N))


def _preprocess_idf(docdb_obj, N):
    # For every unique token, obtained from list of tokens whose tf has been
    # computed
    for token in docdb_obj.tf.keys():
        # Number of documents that have that token
        num_doc = len(docdb_obj.tf[token])
        # Calculate IDF (N = total number of documents)
        docdb_obj.idf[token] = 1 + math.log10(N / num_doc + 1)


def _preprocess_magnitude(docdb_obj):
    magnitudes = [0 for i in range(len(docdb_obj.id_list))]
    # The magnitude of the vectors of every document is dependent on the
    # terms it contains only
    for term in docdb_obj.tf.keys():
        for (docnum, tf) in docdb_obj.tf[term]:
            magnitudes[docnum] += (docdb_obj.idf[term] * tf)**2
    for docnum in range(len(docdb_obj.id_list)):
        magnitudes[docnum] = magnitudes[docnum]**0.5
    for term in docdb_obj.tf.keys():
        for i in range(len(docdb_obj.tf[term])):
            (docnum, tf) = docdb_obj.tf[term][i]
            docdb_obj.tf[term][i] = (docnum, tf / magnitudes[docnum])


def preprocess():
    # Empty list of documents
    documents = []
    # Empty list of directories
    directories = []
    # List the root directory of the corpus
    dir_list = listdir(global_vars._DOCS_PATH)
    # Add all the documents to the documents list
    documents += [f for f in dir_list if isfile(
        path.join(global_vars._DOCS_PATH, f)) and f != ".pyirdocs.db"]
    # Add all the directories to the directories list
    directories += [d for d in dir_list if isdir(
        path.join(global_vars._DOCS_PATH, d))]
    # While there are still directories left to evaluate
    while len(directories) > 0:
        # Obtain absolute parth to the directory
        abs_dir = os.path.join(global_vars._DOCS_PATH, directories[0])
        # List the contents of the directory
        dir_list = os.listdir(abs_dir)
        # Append all documents to the documents list above
        documents += [os.path.join(directories[0], f) for f in dir_list
                      if isfile(os.path.join(abs_dir, f))]
        # Append all directories to the directories list above
        directories += [os.path.join(directories[0], d) for d in dir_list
                        if isdir(os.path.join(abs_dir, d))]
        # Trim off the first directory
        directories = directories[1:]
    # A list of tuples of (docID, docName)
    doc_list = []
    # Fill up the above tuple
    for i in range(len(documents)):
        doc_list.append((i, documents[i]))
    # Create a DocDB object with the above list of tuples
    docdb_obj = document.DocDB(doc_list)
    # For every document
    for i in range(len(documents)):
        # Tell user we're processing it
        print("Processing " + documents[i] + "...")
        # And fill up the tf table for using it
        _preprocess_file(i, docdb_obj, documents[i])
    # Tell user we're almost done
    print("Finishing up...")
    # Compute idf for every word
    _preprocess_idf(docdb_obj, len(documents))
    # And compute magnitude for every document
    _preprocess_magnitude(docdb_obj)
    # And load the object to the global variable
    global_vars._DOC_DB_OBJ = docdb_obj
    # The file to write to
    out_file = path.join(global_vars._DOCS_PATH, ".pyirdocs.db")
    # Picle the class to the file
    pickle.dump(docdb_obj, open(out_file, "wb"))
    # And now tell them we're done
    print("Done.\n\n")
