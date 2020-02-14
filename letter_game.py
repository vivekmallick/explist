import curses

list_of_names = [
        'Apple',
        'Ball',
        'Cat',
        'Dog',
        'Elephant',
        'Fall',
        'Grape',
        'Hat',
        'Icecream',
        'Jog',
        'Kite',
        'Log',
        'Moss',
        'Net',
        'Omlette',
        'Pill',
        'Queen',
        'Red',
        'Sit',
        'Tim',
        'Uma',
        'Vim',
        'Week',
        'X-ray',
        'Yo-yo',
        'Zebra'
        ]


def gap_to_center_str(width, s):
    ls = len(s)
    if ls >= width:
        s = s[:width-1]
        s = s + '-'
        ls = len(s)

    gap = width - ls
    initgap = gap // 2
    return (initgap, s)

def center_string(win, row, s) :
    wc = curses.COLS
    g, s = gap_to_center_str(wc, s)
    ls = len(s)
    win.addnstr(row, g, s, ls)

def left_string(win, row, s) :
    wc = curses.COLS
    ls = len(s)
    if ls >= wc :
        s = s[:wc-1]
        s = s + '-'
        ls = len(s)
    win.addnstr(row, 0, s, ls)

def curse_game(a):
    w = curses.initscr()
    curses.cbreak()
    curses.noecho()
    w.clear()
    wl = curses.LINES
    wc = curses.COLS

    if wl > 12 and wc > 50:
        s = 'Welcome to screen'
        center_string(w, 2, s)

        f = 'Some interesting footer'
        fl = 'Help'
        center_string(w, wl - 2, f)
        left_string(w, wl - 2, fl)

    a = w.getch()
    ca = chr(a)
    w.move(wl -1, wc - 1)
    lca = 1
    while a != ord('Q') :
        center_string(w, wl // 2, lca * ' ')
        lca = len(ca)
        center_string(w, wl // 2, ca)
        w.move(wl -1, wc - 1)
        a = w.getch()
        if a >= ord('a') and a <= ord('z') :
            n = a - ord('a')
            ca = chr(a + (ord('A') - ord('a'))) + ': ' + list_of_names[n]
        else :
            ca = chr(a)

    curses.nocbreak()
    curses.echo()
    curses.endwin()
    del w

curses.wrapper(curse_game)
