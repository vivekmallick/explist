#!/usr/bin/python3

import curses
import random

def play_game(place_holder) :
    # Setup
    win = curses.initscr()
    curses.cbreak()
    curses.noecho()
    # The game
    no_rows = curses.LINES
    no_cols = curses.COLS
    initpos_r = random.randint(0, no_rows-1)
    initpos_c = random.randint(0, no_cols-1)
    pos_r = initpos_r
    pos_c = initpos_c
    win.clear()
    win.move(pos_r, pos_c)
    win.addch('*')
    cmd = ''
    pc = '*'
    while cmd != 'Q' :
        cmd = win.getkey()
        if cmd == "KEY_UP" or cmd == 'k' :
            pos_r = pos_r - 1
            if pos_r < 0 :
                pos_r = no_rows - 1
        elif cmd == "KEY_DOWN" or cmd == 'j' :
            pos_r = pos_r + 1
            if pos_r >= no_rows :
                pos_r = 0
        elif cmd == "KEY_RIGHT" or cmd == 'l' :
            pos_c = pos_c + 1
            if pos_c >= no_cols :
                pos_c = 0
        elif cmd == "KEY_LEFT" or cmd == 'h' :
            pos_c = pos_c - 1
            if pos_c < 0 :
                pos_c = no_cols - 1
        else :
            pc = cmd[0]
        win.addstr(0, 0, str((pos_r, pos_c)))
        win.move(pos_r, pos_c)
        win.addch(pc)
        win.move(pos_r, pos_c)
        win.refresh()
    # Wind up
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    del win

curses.wrapper(play_game)
curses.echo()
curses.nocbreak()
curses.endwin()
