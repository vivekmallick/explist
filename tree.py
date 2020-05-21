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

class Tree :
    def __init__(cls, scr) :
        cls.parent = 'p'
        cls.t = [(0, 'r', [(cls.parent, str(0))])]
        cls.cid = 0 # cid = current id
        cls.s = scr

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
        return i

    def __str__(cls) :
        tv = ''
        for lf in cls.t :
            tv += str(lf[0]) + ': ' + lf[1]
            tv += ', parent = ' + lf[2][0][1]
            tv += ', props: ' + str(lf[2][1:])
            tv += '\n'
        return tv

    def __repr__(cls) :
        tv = ''
        for lf in cls.t :
            tv += str(lf[0]) + ': ' + lf[1]
            tv += ', props ---- '
            for p in lf[2] :
                tv += '[' + p[0] + ' = ' + p[1] + ']'
            tv += '\n'
        return tv

    def name(cls) :
        return cls.t[cls.loc_of_id(cls.cid)][1]

    def name_at_id(cls, i) :
        return cls.t[cls.loc_of_id(i)][1]

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
            tree_error_screen(cls.s, 'loc_of_id', 'invalid id ' + str(i), 3)
            loc = cls.cid
        return loc

    def mod_name_at_id(cls, i, new_name) :
        l = cls.loc_of_id(i)
        id_at_i, name_at_i, prop_at_i = cls.t[l]
        if id_at_i == i :
            new_obj = (id_at_i, new_name, prop_at_i)
            cls.t[l] = new_obj
        else :
            tree_error_screen(cls.s, 'mod_name_at_id',
                    'unexplained_error. critical bug', 3)

    def mod_name(cls, new_name) :
        cls.mod_name_at_id(cls.cid, new_name)

    def rmlf(cls, i) :
        l = cls.loc_of_id(i)
        del cls.t[l]

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

    def add_property_at_loc(cls, loc, key, value, inform_key_repeat = True) :
        loc_id = cls.t[loc][0]
        loc_st = cls.t[loc][1]
        prps   = cls.t[loc][2]
        success = False
        repeated_key = False
        for prp in prps :
            if prp[0] == key :
                repeated_key = True
        if repeated_key :
            if inform_key_repeat :
                tree_error_screen(cls.s, "add_property_at_loc", "property" +
                        " already exists. no changes made at id " +
                        str(loc_id) + ": " + loc_st + ".", 1)
        else :
            prps.append((key, value))
            cls.t[loc] = (loc_id, loc_st, prps)
            success = True
        return success

    def add_property_at_id(cls, i, key, value, inform_key_repeat = True) :
        return cls.add_property_at_loc(cls.loc_of_id(i), key, value,
                inform_key_repeat)

    def add_property(cls, key, value, inform_key_repeat = True) :
        return add_property_at_id(cls.cid, key, value, inform_key_repeat)

    def mod_property_at_loc(cls, l, key, value) :
        l_id = cls.t[l][0]
        l_st = cls.t[l][1]
        l_pr = cls.t[l][2]
        found_key = False
        pos_key = -1
        while (not found_key) and pos_key < len(l_pr) - 1 :
            pos_key += 1
            if l_pr[pos_key][0] == key :
                found_key = True
        if found_key :
            l_pr[pos_key] = (key, value)
            cls.t[l] = (l_id, l_st, l_pr)
        else :
            tree_error_screen(cls.s, "mod_property_at_loc", "property " +
                    key + " not found at id " + str(l_id) + ": " + l_st +
                    ".", 1)
        return found_key

    def mod_property_at_id(cls, i, key, value) :
        return cls.mod_property_at_loc(cls.loc_of_id(i), key, value)

    def mod_property(cls, key, value) :
        return cls.mod_property_at_id(cls.cid, key, value)

    def add_or_mod_property_at_loc(cls, l, key, value) :
        succ = cls.add_property_at_loc(l, key, value, inform_key_repeat =
                False)
        if not succ :
            succ = cls.mod_property_at_loc(l, key, value)
        return succ

    def add_or_mod_property_at_id(cls, i, key, value) :
        return cls.add_or_mod_property_at_loc(cls.loc_of_id(i), key, value)

    def add_or_mod_property(cls, key, value) :
        return cls.add_or_mod_property_at_id(cls.cid, key, value)

    def list_id_prop_eq_val(cls, key, value) :
        lpv = []
        for loc in range(len(cls.t)) :
            val_at_loc = cls.value_property_at_loc(loc, key)
            if val_at_loc == value :
                lpv.append(cls.id_at_loc(loc))
        return lpv
        # Continue from here

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
    scr = screen.Screen(15, 40)
    tt = Tree(scr)
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
    print(tt.__repr__())

    print('Checking value-property')
    print('=======================')
    print(tt.value_property_at_id(3, 'e'))
    print(tt.value_property_at_id(4, 'i'))

    print('Checking add-property')
    print('=====================')
    tt.add_property_at_id(3, 'i', 'Hello')
    tt.add_property_at_id(4, 'i', 'Hello')
    print(tt.__repr__())

    print('Checking mod-property')
    print('=====================')
    tt.mod_property_at_id(0, 'i', 'Hello')
    tt.mod_property_at_id(4, 'i', 'Hello')
    print(tt.__repr__())

    print('Checking add-or-mod-property')
    print('============================')
    tt.add_or_mod_property_at_id(4, 'i', 'Cards')
    tt.add_or_mod_property_at_id(2, 'i', 'Cards')
    print(tt.__repr__())
    
    print('Checking name and list_id_prop_eq_val')
    print('=====================================')
    lt = tt.list_id_prop_eq_val('i', 'Cards')
    print(lt)
    for i in lt :
        print(tt.name_at_id(i), end=' ')
    print()
    for i in lt:
        tt.move_to_id(i)
        print(tt.name(), end=' ')
    print()
