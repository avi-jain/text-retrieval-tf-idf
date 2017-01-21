#######################################################################
# INITIALIZATION MODULE
#######################################################################

# This is the initialization module of our project. It has functionality
# for the initial configuration of the database for the first run of the
# search engine.

# First, we need to read a config file (if it exists), else create it.
# The config file will be stored as ~/.pyirconf
# This config file will basically contain the following information -
# 1) Path to the directory where all the documents are located
# 2) Path to the location where the .pyirdocs.db file is stored

# As of now, this module recommends the use of the following interfaces ->
#
# FUNCTIONS -
#
# init() - This sets up the initial configuration file for the project
#          in an interactive manner. It also parses the initial database
#          and creates a .pyirdocs.db at a location specified by the user.
#          This file would be the result of parsing the database and would
#          contain strucutes (like the inverted index) which would help us
#          in our search

#######################################################################
# External libraries we'll be using
#######################################################################

# We need to use this for stuff like checking for the existence of files
import os

# We need this for writing to the file as a binary file
import pickle

#######################################################################
# Modules of out own project
#######################################################################

# Module which stores global variables for easier configuration
import global_vars

# Module which performs the required preprocessing on the documents
# and generates the .pyirdocs.db file
import preprocessor

#######################################################################
# FUNCTIONS
#######################################################################


def _initconf():
    # Print the welcome message for the configuration screen
    print("\nWelcome to {} configuration.\n".format(global_vars._NAME)
          + "Let's set up search.")

    # Ask to be pointed to the location of corpus
    print("First, we need you to point us to the root of the database.")
    docs_path = input("Path to database: ").strip()

    # If required, modify directory path and add '/' at the end
    if docs_path[-1] != '/':
        docs_path += '/'

    # Get absolute path
    docs_path = os.path.expanduser(docs_path)

    # Write to the configuration file
    of_obj = open(global_vars._CONF_PATH, "w")
    of_obj.write("DOCS_PATH {}\n".format(docs_path))
    of_obj.close()

    # Tell user that file was successfully written
    print("~/.pyirconf successfully written.\n")


def _initdb():
    if os.path.exists(global_vars._DOCS_PATH) and os.path.isdir(
            global_vars._DOCS_PATH):
        preprocessor.preprocess()
        return 0
    else:
        c = input("Could not create the database file. " +
                  "Do you wish to reconfigure? (y/n)")
        if c not in ["n", "N"]:
            return 1
        else:
            print("We cannot continue without the database file. Aborting..")
            quit()


def init():
    # Initialize global variables
    global_vars._NAME = "SEARCH ENGINE"
    global_vars._VERSION = "0.0.1"
    global_vars._AUTHORS = ["Budakausik Vedula",
                            "Shreyas Pandey",
                            "Avi Jain",
                            "Aman Gupta",
                            "Srimanta Barua"]
    global_vars._LICENSE = ""
    global_vars._CONF_PATH = os.path.expanduser("~/.pyirconf")

    # Print welcome message
    print("\n{} version {}.".format(global_vars._NAME, global_vars._VERSION))
    print("AUTHORS: {}".format(", ".join(global_vars._AUTHORS)))

    # Check if the config file (~/.pyirconf) exists
    if not (os.path.exists(global_vars._CONF_PATH)
            and os.path.isfile(global_vars._CONF_PATH)):
        # If not, ask if user wants to create it
        print("\nYou seem to not have a ~/.pyirconf file.")
        print("This file is needed for the search functionality.")
        c = input("Create ~/.pyirconf now? (y/n) ")
        if c not in ["n", "N"]:
            # If yes, create it
            _initconf()
        else:
            # Else, exit
            print("Cannot continue without a valid ~/.pyirconf. Exiting...")
            quit()

    # Open the configuration file
    if_obj = open(global_vars._CONF_PATH, "r")

    # Extract the path to the documents
    global_vars._DOCS_PATH = if_obj.readline().strip().split()[1]

    # If required, append a '/' to the end of the directory
    if global_vars._DOCS_PATH[-1] is not '/':
        global_vars._DOCS_PATH += '/'

    # Close the file object
    if_obj.close()

    # Get path to the .pyirdocs.db file
    db_path = global_vars._DOCS_PATH + ".pyirdocs.db"

    # If the file does not exist
    while not (os.path.exists(db_path) and os.path.isfile(db_path)):
        # While the _initdb() function does not return status 'valid'
        if _initdb() != 0:
            # Redo configuration
            _initconf()

            # Open the configuration file
            if_obj = open(global_vars._CONF_PATH, "r")

            # Extract the path to the documents
            global_vars._DOCS_PATH = if_obj.readline().strip().split()[1]

            # If required, append a '/' to the end of the directory
            if global_vars._DOCS_PATH[-1] is not '/':
                global_vars._DOCS_PATH += '/'

            # Close the file object
            if_obj.close()

            # Get path to the .pyirdocs.db file
            db_path = global_vars._DOCS_PATH + ".pyirdocs.db"

    global_vars._DOC_DB_OBJ = pickle.load(open(db_path, "rb"))
