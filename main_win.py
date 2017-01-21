#######################################################################
# THE DISPLAY MODULE
#######################################################################

# This module sets up the GUI, using Python bindings for unicurses

#######################################################################
# External modules we use
#######################################################################

from unicurses import *

import os

import sys

#######################################################################
# Modules of our own project
#######################################################################

# The initialization module
import init
import voice_recog
# The query module
import query

# Global variables
import global_vars

#######################################################################
# Classes
#######################################################################

#######################################################################
# Functions
#######################################################################

def exec_command(command):
    if command[0] == ':':
        command = command[1:]
        if command == 'v':
            return voice_recog.recog()
        elif command == 'q':
            nocbreak()
            keypad(False)
            echo()
            endwin()
            quit()


def open_file(file_name):
    abs_name = global_vars._DOCS_PATH + file_name
    if os.path.exists(abs_name) and os.path.isfile(abs_name):
        if sys.platform == "win32":
            os.system("notepad.exe " + abs_name)
        elif sys.platform == "linux" or sys.platform == "linux2":
            os.system('%s %s' % (os.getenv('EDITOR'), abs_name))


def display_init():
    # Start
    stdscr = initscr()
    clear()
    noecho()
    cbreak()
    keypad(stdscr, True)

    header = ["***********************************************************************",
              global_vars._NAME,
              "AUTHORS : " + ', '.join(global_vars._AUTHORS),
             "***********************************************************************"]

    instructions = ["INSTRUCTIONS :",
                    "1) Type to search",
                    "2) Use the arrow keys to select the required file",
                    "3) DO NOT resize the window",
                    "4) Press Enter when a file is selected to open it.",
                    "5) Press Esc to exit."]

    directory = "DIRECTORY : {}".format(global_vars._DOCS_PATH)

    prompt = "Search: "
    str_1 = ""
    str_2 = ""

    move(5, 5)

    query.query("Hello")

    search_linum = 14
    display_linum = 16

    res = []

    selected = 0

    command_mode = False
    command_str_1 = ""
    command_str_2 = ""

    while (True):
        y, x = getmaxyx(stdscr)

        clear()

        mvwaddstr(stdscr,0, 5, header[0])
        mvwaddstr(stdscr,1, 5, header[1])
        mvwaddstr(stdscr,2, 5, header[2])
        mvwaddstr(stdscr,3, 5, header[3])

        mvwaddstr(stdscr,5, 5, instructions[0])
        mvwaddstr(stdscr,6, 5, instructions[1])
        mvwaddstr(stdscr,7, 5, instructions[2])
        mvwaddstr(stdscr,8, 5, instructions[3])
        mvwaddstr(stdscr,9, 5, instructions[4])
        mvwaddstr(stdscr,10, 5, instructions[5])

        mvwaddstr(stdscr,12, 5, directory)

        linum = display_linum

        # Display the documents. Highlight the one selected
        if len(res) > 0:
            for (doc, score) in res[0:selected]:
                mvwaddstr(stdscr,linum, 7, doc)
                linum += 1
            mvwaddstr(stdscr,linum, 7, res[selected][0], A_REVERSE)
            linum += 1
            for (doc, score) in res[selected + 1:10]:
                mvwaddstr(stdscr,linum, 7, doc)
                linum += 1

        mvaddstr(stdscr, y - 1, command_str_1 + command_str_2)
        mvwaddstr(stdscr,search_linum, 5, prompt + str_1 + str_2)

        if command_mode:
            move(y - 1, 5 + len(command_str_1))
        else:
            move(search_linum, 5 + len(prompt) + len(str_1))

        refresh()

        ch = getch()

        # Deal with resize first
        if ch == KEY_RESIZE:
            pass
        # Backspace
        elif ch == 8:
            if command_mode:
                command_str_1 = command_str_1[:-1]
            else:
                str_1 = str_1[:-1]
        # Enter
        elif ch == 10:
            if command_mode:
                command_mode = False
                str_1 = exec_command(command_str_1 + command_str_2)
                str_2 = ""
                command_str_1 = ""
                command_str_2 = ""
            else:
                open_file(res[selected][0])
                clear()
                noecho()
                cbreak()
                keypad(stdscr,True)
        # Excape
        elif ch == 27:
            if command_mode:
                command_str_1 = ""
                command_str_2 = ""
                command_mode = False
                continue
            else:
                break
        # Delete
        elif ch == KEY_DC:
            if command_mode:
                command_str_2 = command_str_2[1:]
            else:
                str_2 = str_2[1:]
        # Left arrow key
        elif ch == KEY_LEFT:
            if command_mode:
                if len(command_str_1) > 0:
                    command_str_2 = command_str_1[-1] + command_str_2
                    command_str_1 = command_str_1[:-1]
            else:
                if len(str_1) > 0:
                    str_2 = str_1[-1] + str_2
                    str_1 = str_1[:-1]
            continue
        # Right arrow key
        elif ch == KEY_RIGHT:
            if command_mode:
                if len(command_str_2) > 0:
                    command_str_1 = command_str_1 + command_str_2[0]
                    command_str_2 = command_str_2[1:]
            else:
                if len(str_2) > 0:
                    str_1 = str_1 + str_2[0]
                    str_2 = str_2[1:]
        # Down arrow key
        elif ch == KEY_DOWN:
            if not command_mode and selected < 9 and selected < len(res) - 1:
                selected += 1
            continue
        # Up arrow key
        elif ch == KEY_UP:
            if not command_mode and selected > 0:
                selected -= 1
            continue
        # Colon for command mode
        elif chr(ch) == ':':
            if not command_mode and len(str_1 + str_2) == 0:
                command_mode = True
                command_str_1 = ':'
                command_str_2 = ''
            elif not command_mode:
                str_1 += chr(ch)
            else:
                command_str_1 += chr(ch)
        # Any other character
        else:
            if command_mode:
                command_str_1 += chr(ch)
            else:
                str_1 += chr(ch)

        selected = 0
        res = query.query(str_1 + str_2)

    # End
    nocbreak()
    keypad(stdscr,False)
    echo()
    endwin()


def default_main():
    while True:
        intext = input()
        if intext == "quit()":
            quit()
        docs = query.query(intext)
        for doc in docs[:10]:
            print(doc[0])

def main():
    init.init()
    display_init()


if __name__ == "__main__":
    main()
