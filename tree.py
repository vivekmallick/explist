#!/usr/bin/python3
import sys
import screen

def tree_error(fnname, errname, sev) :
    error_str = fnname + ':' + ' ' * (19 - len(fnname))
    error_str += errname
    if sev == 0 :
        error_str = 'Debug:' + error_str
    if sev == 1 :
        error_str = 'Info: ' + error_str
    if sev == 2 :
        error_str = 'Warn: ' + error_str
    if sev == 3 :
        error_str = 'Error:' + error_str
    if sev == 4 :
        error_str = 'Crit: ' + error_str
    print(error_str)
    if sev >= 3 :
        sys.exit('tree_error: triggering exit')
    return error_str

def tree_error_screen(scrn, fnname, errname, sev) :
    if sev == 0 :
        error_type = 'Debug'
    if sev == 1 :
        error_type = 'Info'
    if sev == 2 :
        error_type = 'Warn'
    if sev == 3 :
        error_type = 'Error'
    if sev == 4 :
        error_type = 'Crit'
    user_input = scrn.scr_error(errname, fnname, 'tree', error_type)
    if sev >= 3 :
        sys.exit('tree_error: triggering exit')
    return user_input

def tree_encode(scr, s) :
    """
    TT = 'T'
    Tb = ' '
    Tn = '\n'
    Tc = ':'
    Td = '$'
    Th = '-'
    """
    ec = ''
    for c in s :
        if c == 'T' :
            ec += 'TT'
        elif c == ' ' :
            ec += 'Tb'
        elif c == '\n' :
            ec += 'Tn'
        elif c == ':' :
            ec += 'Tc'
        elif c == '$' :
            ec += 'Td'
        elif c == '-' :
            ec += 'Th'
        else :
            ec += c
    return ec

def tree_decode(scr, es) :
    s = ''
    foundT = False
    for c in es :
        if foundT :
            foundT = False
            if c == 'T' :
                s += 'T'
            elif c == 'b' :
                s += ' '
            elif c == 'n' :
                s += '\n'
            elif c == 'c' :
                s += ':'
            elif c == 'd' :
                s += '$'
            elif c == 'h' :
                s += '-'
            else :
                ev = tree_error_screen(scr, 'tree_decode', 'Unknown T command:' + c, 2)
                s += ev
        else :
            if c == 'T' :
                foundT = True
            else :
                s += c
    return s

def lftostr(scr, lf) :
    lfid = str(lf[0])
    lfstr = tree_encode(scr, lf[1])
    lfprp = ''
    for lp in lf[2] :
        lps = tree_encode(scr, lp[0]) + '-' + tree_encode(scr, lp[1])
        if lfprp == '' :
            lfprp = lps
        else :
            lfprp += '$' + lps
    return (lfid + ':' + lfstr + ':' + lfprp)

def strtolf(scr, s) :
    lftriple = s.split(':')
    if len(lftriple) != 3:
        tree_error_screen(scr, 'strtolf', 'Badly formed leaf-string', 4)
    else :
        lfid = int(lftriple[0])
        lfstr = tree_decode(scr, lftriple[1])
        lfprp = []
        prpstrs = lftriple[2].split('$')
        for prpstr in prpstrs :
            prppair = prpstr.split('-')
            if len(prppair) != 2 :
                tree_error_screen(scr, 'strtolf', 'Badly formed property str', 4)
            else :
                lfprp.append((tree_decode(scr, prppair[0]), tree_decode(scr, prppair[1])))
    return (lfid, lfstr, lfprp)

class Tree() :
    def __init__(cls) :
        cls.parent = 'p'
        cls.t = [(0, 'r', [(cls.parent, str(0))])]
        cls.cid = 0 # cid = current id
        cls.s = screen.Screen(15, 40)

    def add(cls, par, st, prps) :
        newprps = [(cls.parent, str(par))]
        newprps = newprps + prps
        indices_used = []
        for lf in cls.t :
            indices_used.append(lf[0])
        found_ind = False
        i = 0
        while not found_ind :
            if i in indices_used :
                i += 1
            else :
                found_ind = True
        cls.t.append((i, st, newprps))

    def __str__(cls) :
        tv = ''
        for lf in cls.t :
            tv += str(lf[0]) + ': ' + lf[1]
            tv += ', parent = ' + lf[2][0][1]
            tv += '\n'
        return tv

    def __repr__(cls) :
        return cls.__str__()

    def id_at_loc(cls, l) :
        return cls.t[l][0]

    def loc_of_id(cls, i) :
        l = 0
        found_id = False
        while (not found_id) and l < len(cls.t) :
            cid = cls.t[l][0]
            if cid == i :
                loc = l
                found_id = True
            l += 1
        if not found_id :
            tree_error_screen(cls.s, 'loc_of_id', 'invalid id', 3)
            loc = cls.cid
        return loc

    def value_property_at_loc(cls, loc, key) :
        prps = cls.t[loc][2]
        retval = None
        for p in prps :
            if p[0] == key :
                retval = p[1]
        return retval

    def value_property_at_id(cls, i, key) :
        return cls.value_property_at_loc(cls.loc_of_id(i), key)

    def value_property(cls, key) :
        return cls.value_property_at_id(cls.cid, key)

    def parentleaf_at_loc(cls, loc) :
        return int(cls.value_property_at_loc(loc, cls.parent))

    def parentleaf_at_id(cls, i) :
        return cls.parentleaf_at_loc(cls.loc_of_id(i))

    def parentleaf(cls) :
        return cls.parentleaf_at_id(cls.cid)

    def list_leaves(cls) :
        ll = []
        for loc in range(len(cls.t)) :
            if cls.parentleaf_at_loc(loc) == cls.cid :
                ll.append(cls.id_at_loc(loc))
        return ll

    def move_to_loc(cls, loc) :
        cls.cid = cls.id_at_loc(loc)

    def move_to_id(cls, i) :
        cls.cid = i

    def save_to_file(cls, fname) :
        with open(fname, 'w') as outf :
            for lf in cls.t :
                print(lftostr(cls.s, lf), file=outf)

    def load_from_file(cls, fname) :
        cls.t = []
        with open(fname, 'r') as inf :
            for l in inf :
                cls.t.append(strtolf(cls.s, l.strip()))
        cls.cid = 0

if __name__ == '__main__' :
    tt = Tree()
    scr = tt.s
    print('Checking encode/decode')
    print('======================')
    text = '12:treentry:p-23$i-23$o-12'
    enctext = tree_encode(scr, text)
    dectext = tree_decode(scr, text)
    print('Ori text:', text)
    print('Enc text:', enctext)
    print('Dec text:', dectext)
    print(tree_decode(scr, 'Trees are nice. There is no doubt. Tobb'))
    print()

    print('Checking tree')
    print('=============')
    tt.add(0, 'Item 1', [(' T$e-s:t', 'A-test$property')])
    tt.add(0, 'Item 2', [])
    tt.add(1, 'Item 1:a', [])
    tt.add(1, 'Item 1:b', [('i', 'Card'), ('x', 'y')])
    tt.t = tt.t[2:] + tt.t[:2]
    print(tt)

    print('Checking lftostr')
    print('================')
    for lf in tt.t :
        print(lf, ' gives')
        lfstr = lftostr(scr, lf) 
        print('lfstr = ', lfstr, ' which comes from')
        print(str(strtolf(scr, lfstr)))

    print()
    tt.move_to_id(0)
    print('Checking parent and list_leaves at tt.cid =', tt.cid, ', loc =', tt.loc_of_id(tt.cid))
    print('===========================================')
    print('Parent:', tt.parentleaf())
    print('Leaves:', tt.list_leaves())

    print('Checking save/load')
    print('==================')
    print('Saving file', end='...')
    tt.save_to_file('treedata.txt')
    print('done')

    print('Loading file', end='...')
    tt.load_from_file('treedata.txt')
    print('done')
    print(tt)

    print('Checking value-property')
    print('=======================')
    print(tt.value_property_at_id(3, 'e'))
    print(tt.value_property_at_id(4, 'i'))
