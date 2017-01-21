#! /use/bin/python3

#######################################################################
# THE DISPLAY MODULE
#######################################################################

# This module sets up the GUI, using Python bindings for GTK3

#######################################################################
# External modules we use
#######################################################################

import curses
from curses import wrapper

import os

import sys

#######################################################################
# Modules of our own project
#######################################################################

# The initialization module
import init

# The query module
import query

# Global variables
import global_vars

# VOice search
import voice_recog

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
            text = voice_recog.recog()
            return query.query(text)
        elif command == 'q':
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()
            quit()


def open_file(file_name):
    abs_name = global_vars._DOCS_PATH + file_name
    if os.path.exists(abs_name) and os.path.isfile(abs_name):
        if sys.platform == "win32":
            os.system(abs_name)
        elif sys.platform == "linux" or sys.platform == "linux2":
            os.system('%s %s' % (os.getenv('EDITOR'), abs_name))


def display_init(stdscr):
    # Start
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    header = ["***********************************************************************",
              global_vars._NAME,
              "AUTHORS : " + ', '.join(global_vars._AUTHORS),
             "***********************************************************************"]

    instructions = ["INSTRUCTIONS :",
                    "1) Type to search",
                    "2) Use the arrow keys to select the required file",
                    "3) DO NO resize the window",
                    "4) Press Enter when a file is selected to open it.",
                    "5) Press Esc to exit."]

    directory = "DIRECTORY : {}".format(global_vars._DOCS_PATH)

    prompt = "Search: "
    str_1 = ""
    str_2 = ""

    stdscr.move(5, 5)

    query.query("Hello")

    search_linum = 14
    display_linum = 16

    res = []

    selected = 0

    command_mode = False
    command_str_1 = ""
    command_str_2 = ""

    while (True):
        y, x = stdscr.getmaxyx()
        if x < 80 and y < 30:
            curses.resizeterm(30, 80)
        elif x < 80:
            curses.resizeterm(y, 80)
        elif y < 30:
            curses.resizeterm(30, x)
        stdscr.refresh()

        stdscr.clear()

        stdscr.addstr(0, 5, header[0])
        stdscr.addstr(1, 5, header[1])
        stdscr.addstr(2, 5, header[2])
        stdscr.addstr(3, 5, header[3])

        stdscr.addstr(5, 5, instructions[0])
        stdscr.addstr(6, 5, instructions[1])
        stdscr.addstr(7, 5, instructions[2])
        stdscr.addstr(8, 5, instructions[3])
        stdscr.addstr(9, 5, instructions[4])
        stdscr.addstr(10, 5, instructions[5])

        stdscr.addstr(12, 5, directory)

        linum = display_linum

        # Display the documents. Highlight the one selected
        if len(res) > 0:
            for (doc, score) in res[0:selected]:
                stdscr.addstr(linum, 7, doc)
                linum += 1
            stdscr.addstr(linum, 7, res[selected][0], curses.A_REVERSE)
            linum += 1
            for (doc, score) in res[selected + 1:10]:
                stdscr.addstr(linum, 7, doc)
                linum += 1

        stdscr.addstr(y - 1, 5, command_str_1 + command_str_2)
        stdscr.addstr(search_linum, 5, prompt + str_1 + str_2)

        if command_mode:
            stdscr.move(y - 1, 5 + len(command_str_1))
        else:
            stdscr.move(search_linum, 5 + len(prompt) + len(str_1))

        stdscr.refresh()

        ch = stdscr.getch()

        # Deal with resize first
        if ch == curses.KEY_RESIZE:
            pass
        # Backspace
        elif ch == 127:
            if command_mode:
                command_str_1 = command_str_1[:-1]
            else:
                str_1 = str_1[:-1]
        # Enter
        elif ch == 10:
            if command_mode:
                command_mode = False
                res = exec_command(command_str_1 + command_str_2)
                command_str_1 = ""
                command_str_2 = ""
            else:
                open_file(res[selected][0])
                stdscr.clear()
                curses.noecho()
                curses.cbreak()
                stdscr.keypad(True)
            selected = 0
            continue
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
        elif ch == curses.KEY_DC:
            if command_mode:
                command_str_2 = command_str_2[1:]
            else:
                str_2 = str_2[1:]
        # Left arrow key
        elif ch == curses.KEY_LEFT:
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
        elif ch == curses.KEY_RIGHT:
            if command_mode:
                if len(command_str_2) > 0:
                    command_str_1 = command_str_1 + command_str_2[0]
                    command_str_2 = command_str_2[1:]
            else:
                if len(str_2) > 0:
                    str_1 = str_1 + str_2[0]
                    str_2 = str_2[1:]
            continue
        # Down arrow key
        elif ch == curses.KEY_DOWN:
            if not command_mode and selected < 9 and selected < len(res) - 1:
                selected += 1
            continue
        # Up arrow key
        elif ch == curses.KEY_UP:
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
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


def main():
    init.init()
    wrapper(display_init)


if __name__ == "__main__":
    main()
