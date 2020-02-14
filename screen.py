#!/usr/bin/python3
import time

def scr_delay(t_in_sec) :
    """
    To ensure delay
    """
    time.sleep(t_in_sec)

def strip_blanks(dw) :
    """
    Clean a string for pretty printing. To be used by split_sentence
    below.
    """
    w = dw.strip()
    mode = 0
    new_w = ''
    for c in w :
        if c == ' ' :
            if mode != 1 :
                mode = 1
                new_w = new_w + ' '
        else :
            if mode == 1 :
                mode = 0
            new_w = new_w + c
    return new_w

def split_word(w, l) :
    """
    In case the word is longer than length l, split it so that
    it can printed across the next few lines. To be used by
    split_sentence below.
    """
    if l <= 1 :
        print('screen: split_word: l has to be >= 2')
        ws = w
    else :
        l = l - 1
        lw = len(w)
        if lw % l == 0 :
            n_parts = lw // l
        else :
            n_parts = (lw // l) + 1
        ws = []
        for i in range(1, n_parts) :
            beg = (i-1)*l
            end = i*l
            ws.append(w[beg:end] + '-')
        ws.append(w[(n_parts - 1)*l:])
    return ws

def split_sentence(gs, l) :
    """
    Format a sentence gs into parts so that each part is
    a string of of length l. To be used by the write_text method
    below.
    """
    s = strip_blanks(gs)
    words = s.split(' ')
    lists = []
    buff = ''
    for w in words :
        if len(buff) + len(w) < l :
            if buff == '' :
                buff = w
            else :
                buff = buff + ' ' + w
        else :
            lists.append(buff)
            buff = ''
            if len(w) <= l :
                buff = w
            else :
                ws = split_word(w, l)
                lws = len(ws)
                for i in range(0, lws-1) :
                    lists.append(ws[i])
                buff = ws[lws-1]
    if buff != '' :
        lists.append(buff)
    return lists

class ScrWin :
    """
    To define a subwindow with topleft corner at (x, y), height h
    and width w.
    """
    def __init__(self, x, y, h, w) :
        self.topleft = (x, y)
        self.winh = h
        self.winw = w

    def __repr__(self) :
        rval = 'Window with top-left= '
        rval = rval + str(self.topleft)
        rval = rval + ', height ' + str(self.winh)
        rval = rval + ' and width ' + str(self.winw)
        return rval

    def __str__(self) :
        return self.__repr__()

    def winht(self) :
        """
        Returns the height of the subwindow.
        """
        return self.winh

    def winwd(self) :
        """
        Returns the width of the subwindow.
        """
        return self.winw

    def offset(self) :
        """
        Returns a tuple defining the top-left coordinates of the
        subwindow.
        """
        return self.topleft

class Screen :
    """
    The main screen class which controls all the material on
    the screen. Coordinates are of the form (row, column) following
    the curses convention.
    """
    def __init__(self, h=15, w=40) :
        self.h = h
        self.w = w
        self.s = h*w*' '

    def __repr__(self) :
        return self.s

    def __str__(self) :
        return self.__repr__()

    def setscreen(self) :
        """
        Used whenever a new screen is created. Functionally
        this is the same as the clear method.
        """
        self.s = self.h * self.w * ' '

    def clear(self) :
        """
        Clears the screen.
        """
        self.s = self.h * self.w * ' '

    def display(self) :
        """
        Displays the screen in a terminal.
        """
        print()
        l = len(self.s)
        print('+' + self.w * '-' + '+')
        for i in range(l) :
            if i % self.w == 0 :
                if i != 0 :
                    print('|')
                print('|', end='')
                print(self.s[i], end='')
            else :
                print(self.s[i], end='')
        print('|')
        print('+' + self.w * '-' + '+')
        
    def incr_ht(self) :
        """
        Increment height by one.
        """
        self.h += 1
        self.setscreen()
        
    def decr_ht(self) :
        """
        Decrement height by one.
        """
        self.h -= 1
        self.setscreen()
        
    def incr_wd(self) :
        """
        Increment width by one.
        """
        self.w += 1
        self.setscreen()
        
    def decr_wd(self) :
        """
        Decrement width by one.
        """
        self.w -= 1
        self.setscreen()
        
    def prch(self, r, c, ch) :
        """
        Print character ch at row r and column c
        """
        if r >= 0 and r < self.h :
            if c >= 0 and c < self.w :
                i = self.w * r + c
                self.s = self.s[:i] + ch + self.s[i+1:]
            else :
                print('screen: prch: Invalid location.')
        else :
            print('screen: prch: Invalid location.')
            
    def prst(self, r, c, st, lth) :
         """
         Print string st in row r starting from column c with
         with the length adjusted to lth: if the length of st
         is smaller, then blanks are padded, else the string
         is truncated.
         """
         ls = len(st)
         if ls < lth :
             st = st + (lth - ls) * ' '
         elif ls > lth :
             st = st[:lth-1] + '+'
         else :
             st = st
         for i in range(lth) :
             self.prch(r, c+i, st[i])

    def define_win(self, tlx, tly, wh, ww) :
        """
        Create a subwindow.
        """
        if tlx + wh <= self.h and tly + ww <= self.w :
            rval = ScrWin(tlx, tly, wh, ww)
        else :
            print('screen: define_win: invalid window paramters')
            rval = ScrWin(0, 0, self.h, self.w)
        return rval

    def win_prch(self, win, r, c, ch) :
        """
        Print character ch in subwindow win, on relative row r
        and relative column c.
        """
        x, y = win.offset()
        ht = win.winht()
        wd = win.winwd()
        if 0 <= r and r < ht and 0 <= c and c < wd :
            self.prch(x + r, y + c, ch)
        else :
            print('screen: win_prch: Invalid location for', ch, '.')
        
    def win_prst(self, win, r, c, st, lth) :
         """
         Print string st in subwindow win in relative row r starting from
         relative column c with with the length adjusted to lth: if the
         length of st is smaller, then blanks are padded, else the string is
         truncated.
         """
 
         ls = len(st)
         if ls < lth :
             st = st + (lth - ls) * ' '
         elif ls > lth :
             st = st[:lth-1] + '+'
         else :
             st = st
         for i in range(lth) :
             self.win_prch(win, r, c+i, st[i])

    def win_center_prst(self, win, line, st) :
        """
        Print st centered on relative row line in window win.
        """
        wd = win.winwd()
        if len(st) > wd :
            print('screen: win_center_prst: string too long.')
        else :
            indent = (wd - len(st)) // 2
            self.win_prst(win, line, indent, st, len(st))

    def win_clear(self, win) :
        """
        Clear subwindow win.
        """
        wht = win.winht()
        wwd = win.winwd()
        for i in range(wht) :
            self.win_prst(win, i, 0, wwd*' ', wwd)

    def write_text(self, win, s) :
        """
        Format and write text s in subwindow win.
        """
        self.win_clear(win)
        wd = win.winwd()
        wh = win.winht()
        poswin = win.offset()
        x = poswin[0]
        y = poswin[1]
        lines = split_sentence(s, wd)
        if len(lines) > wh :
            print('screen: write_text: string does not fit the window.')
            r = 0
            for l in lines[:wh-1] :
                self.prst(x + r, y, l, wd)
                r += 1
            self.prst(x + r, y, wd*'+', wd)
        else :
            r = 0
            for l in lines :
                self.prst(x + r, y, l, wd)
                r += 1

    def scr_error(self, e, efn, emod, etype) :
        """
        This will be the standard format for errors e in function efn
        in module emod of type etype.
        """
        etype = '*' + etype + '*'
        self.clear()
        lenhead = len(etype) + 1
        head_indent = (self.w - lenhead) // 2
        head_win = self.define_win(1, 0, 1, self.w)
        self.win_clear(head_win)
        self.win_prst(head_win, 0, head_indent, etype, lenhead)

        err_win = self.define_win(4, 2, self.h - 6, self.w - 4)
        self.write_text(err_win, emod)
        err_win = self.define_win(6, 4, self.h - 8, self.w - 6)
        self.write_text(err_win, efn)
        err_win = self.define_win(8, 6, self.h - 10, self.w - 8)
        self.write_text(err_win, e)
        print(etype + ': ' + emod + ': ' + efn + ': ' + e)
        self.display()
        return input('Error: ')

    def scr_input(self, msg, prompt) :
        """
        For user interaction: explain what is needed in message msg, and
        set the prompt to prompt.
        """
        self.clear()
        head_win = self.define_win(1, 0, 1, self.w)
        self.win_center_prst(head_win, 0, 'Input')
        msg_win = self.define_win(4, 2, self.h - 6, self.w - 4)
        self.write_text(msg_win, msg)
        self.display()
        return input(prompt)

if __name__ == '__main__':
    import random
    s = Screen(15, 41)
    s.clear()
    s.display()
    cmd = input('screen> ')
    ii = s.h // 2
    jj = s.w // 2
    while cmd != 'exit' :
        if cmd == 'h+' :
           s.incr_ht()
        elif cmd == 'h-' :
            s.decr_ht()
        elif cmd == 'w+' :
            s.incr_wd()
        elif cmd == 'w-' :
            s.decr_wd()
        elif cmd == 'ss' :
            ht = int(input('Height: '))
            wd = int(input('Width : '))
            s.h = ht
            s.w = wd
            s.setscreen()
        elif cmd == 'cl' :
            s.clear()
        elif cmd == 'an' :
            sg = input('string > ')
            lsg = min(len(sg), s.w)
            sr = s.h // 2
            sc = (s.w - lsg) // 2
            s.prst(sr, sc, sg, lsg)
        elif cmd == 'cw' :
            shrink = int(input('shrink > '))
            mywin = s.define_win(shrink, shrink, s.h - 2*shrink, s.w - 2*shrink)
        elif cmd == 'sh' :
            sent = input('Shout what? ')
            s.write_text(mywin, sent)
        elif cmd == 'er' :
            errtype = input('Error type> ')
            errmod = input('Module> ')
            errfn = input('Function> ')
            error = input('Error> ')
            s.scr_error(error, errfn, errmod, errtype)
        elif cmd == 'in' :
            imess = s.scr_input('Input the input message', 'message> ')
            prompt = s.scr_input('What prompt would you like?', 'prompt> ')
            inpval = s.scr_input(imess, prompt)
            out_win = s.define_win(0, 0, s.h, s.w)
            s.write_text(out_win, inpval)
        else :
            cc = 'm'
            for ijkl in range(100) :
                ii = (ii + random.randint(-1,1)) % s.h
                jj = (jj + random.randint(-1,1)) % s.w
                cc = chr((random.randint(-1,1)+ord(cc) - ord('a'))%26 + ord('a'))
                s.prch(ii, jj, cc)
                s.display()
        s.display()
        cmd = input('screen> ')

