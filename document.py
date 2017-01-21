#######################################################################
# THE DOCUMENT MODULE
#######################################################################

# This module is named "document" for lack of a better name, really.
# It defines an interface for representing information about documents
# in the .pyirdocs.db file.

# Basically it defines a class DocDB, of which only one instance would
# be stored in the .pyirdocs.db file. The decision to make this a class
# was taken just in order to continue with the philosophy of modularity
# that we have adopted, and so as to group similar functionality and
# data together

# The members of the class are -
#
# id_list - This is a list of tuples of (docID, docName). We use this
#           for translations from docID to docName
#
# idf - This is a Python dictionary, This dictionary would be indexed by
#       all the normalized words. Each word would be mapped to a float
#       value which would represent the idf of the word for the collection
#       of documents
#
# tf - This is a Python dictionary. This dictionary would be indexed by
#      all the normalized words. Each word would be mapped to a list of
#      tuples of (docID, tf)

#######################################################################
# CLASS
#######################################################################


class DocDB(object):
    def __init__(self, id_list):
        self.id_list = id_list
        self.idf = {}
        self.tf = {}
