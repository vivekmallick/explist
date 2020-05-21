#!/usr/bin/python3

import sys
import screen
import tree
import list_scr

class ExpTree :
    def __init__(et, scr, cmds = []) :
        et.cmds = cmds + []
        et.tree = tree.Tree(scr)
        et.settings_at = 0
        et.head_at = 0
        et.scr = scr
        et.lscr = list_scr.ListScr(scr, et.cmds + [
            ('u', 'go up'),
            ('q', 'quit seln')
            ], [])
        # Property shortcuts
        et.price = 'r'
        et.pay_source = 's'
        et.conv_rate = 'c'
        et.set_curr_pos(et.head_at)

    def et_error(et, fname, errname, sev) :
        if sev == 0 :
            err_type = 'Debug'
        elif sev == 1 :
            err_type = 'Info'
        elif sev == 2 :
            err_type = 'Warn'
        else :
            err_type = 'Critical'
        user_inp = et.lscr.scr.scr_error(errname, fname, 'exptree',
                err_type)
        if sev > 2 :
            sys.exit('exptree: crash induced by critical error.')
        return user_inp

    def first_run(et) :
        et.settings_at = et.tree.add(0, 'settings', [])
        et.head_at = et.tree.add(0, 'head', [
            (et.price, '0'),
            (et.conv_rate, '1'),
            (et.pay_source, '0')
            ]
            )
        et.tree.add(2, 'banks', [
            (et.price, '0'),
            (et.conv_rate, '1'),
            (et.pay_source, '2')
            ]
            )
        et.tree.add(2, 'exp', [
            (et.price, '0'),
            (et.pay_source, '3'),
            (et.conv_rate, '1')
            ]
            )
        return None

    def load_from_file(et, fname) :
        et.tree.load_from_file(fname)
        et.set_curr_pos(0)
        (kds, ss) = et.current_list()
        headAt = -1
        setAt = -1
        l = 0
        while (headAt == -1 or setAt == -1) and l < len(kds) :
            if et.item_at_id(kds[l]) == 'head' :
                headAt = l
            if et.item_at_id(kds[l]) == 'settings' :
                setAt = l
            l += 1
        if headAt == -1 :
            et.et_error('load_from_file', 'no head found', 3)
        elif setAt == -1 :
            et.et_error('load_from_file', 'no settings found', 3)
        else :
            et.head_at = kds[headAt]
            et.settings_at = kds[setAt]

    def safe_loader(et, fname) :
        file_OK = True
        try :
            expinfl = open(fname, 'r')
            expinfl.close()
        except FileNotFoundError :
            et.et_error('safe_loader', 'no file found. starting over.', 1)
            et.first_run()
            file_OK = False

        if file_OK :
            et.load_from_file(fname)

    def save_to_file(et, fname) :
        et.tree.save_to_file(fname)

    def curr_pos(et) :
        return et.tree.cid

    def set_curr_pos(et, i) :
        et.tree.cid = i

    def is_id_leaf(et, i) :
        were_at = et.curr_pos()
        et.set_curr_pos(i)
        no_leaves_at_id = len(et.tree.list_leaves())
        rval = (no_leaves_at_id == 0)
        et.set_curr_pos(were_at)
        return rval

    def is_leaf(et) :
        no_leaves_at_id = len(et.tree.list_leaves())
        return (no_leaves_at_id == 0)

    def show_leaf_at_id(et, i, prompt) :
        nm = et.item_at_id(i)
        pr = et.price_of_id(i)
        sc = et.item_at_id(et.pay_source_at_id(i))
        cr = et.tree.value_property_at_id(i, et.conv_rate)
        wd = et.scr.w
        ht = et.scr.h
        reply = 'o'
        if ht < 5 or wd < 20 :
            et.et_error('show_leaf_at_id', 'Window too small', 3)
        else :
            while reply == 'o' :
                et.lscr.scr.clear()
                header = et.scr.define_win(0, 0, 1, wd)
                et.lscr.scr.win_center_prst(header, 0, nm)
                et.lscr.scr.prst(2, 0, "  Price: " + str(pr), wd)
                et.lscr.scr.prst(3, 0, "  Pay Source: " + sc, wd) 
                et.lscr.scr.prst(5, 0, "  Conversion: " + str(cr), wd)
                opt_pg = et.lscr.create_footer()
                et.lscr.scr.display()
                reply = input(prompt)
                if reply == 'o' :
                    et.lscr.footer_pos += opt_pg
                    if et.lscr.footer_pos > len(et.lscr.cmds) :
                        et.lscr.footer_pos = 0
        return reply

    def conv_rate_of_id(et, i) :
        try :
            cr = float(et.tree.value_property_at_id(i, et.conv_rate))
        except :
            et.et_error('conv_rate_of_id', 'Invalid conv_rate at id' +
                    str(i), 1)
            cr = 1.0
        return cr

    def price_of_id(et, i) :
        try :
            item_price = float(et.tree.value_property_at_id(i, et.price))
        except :
            et.et_error('price_of_id', 'Invalid value at id: ' + str(i), 1)
            item_price = 0
        return item_price

    def price_at_pos(et) :
        return float(et.tree.value_property(et.price))

    def item_at_id(et, i) :
        return et.tree.name_at_id(i)

    def item(et) :
        return et.tree.name()

    def pay_source_at_id(et, i) :
        return int(et.tree.value_property_at_id(i, et.pay_source))

    def pay_source(et) :
        return int(et.tree.value_property(et.pay_source))

    def current_list(et) :
        """
        Gets all the children of node and lists them under expenditure,
        also lists every entry with node as pay_source and marks them
        negative.
        """
        kids = et.tree.list_leaves()
        # For the following we need a function in tree.py which lists all
        # nodes with certain value for a given property. Let us call this
        # list_id_prop_eq_val
        pysrc = et.tree.list_id_prop_eq_val(et.pay_source, str(et.curr_pos()))
        full_list = (kids, pysrc)
        # Write a code to return a list in the correct format.
        return full_list

    def print_current_list(et, width) :
        kd, sr = et.current_list()
        scl = []
        for i in kd :
            # print('debug: current_list: kd sec:', i)
            pri = et.price_of_id(i)
            itm = et.item_at_id(i)
            itm_width = width - 8
            istr = "{0:{w}s}{1:8.2f}".format(itm, pri, w=itm_width )
            scl.append(istr)
        for i in sr :
            # print('debug: current_list: sr sec:', i)
            pri = 0 - et.price_of_id(i)
            itm = et.item_at_id(i)
            itm_width = width - 8
            istr = "{0:{w}s}{1:8.2f}".format(itm, pri, w=itm_width )
            scl.append(istr)
        return scl

    
    def choose_item(et, prompt="ExpT> ") :
        # choose an item from current list, and set curr_id to that
        kd, _ = et.current_list()
        pricelist = []
        for i in kd :
            pri = et.price_of_id(i)
            itm = et.item_at_id(i)
            pay = et.item_at_id(et.pay_source_at_id(i))[:3]
            width = et.scr.w
            itm_width = width - 8 - 5 - 7
            istr = "{0:{w}s}{1:8.2f} ({2:3s})".format(itm, pri, pay,
                    w=itm_width)
            pricelist.append(istr)
        et.lscr.lst = pricelist
        et.lscr.title = et.item()
        c, s = et.lscr.list_interact(prompt)
        if c == 'selected' :
            val = kd[s]
        else :
            val = -1
        return (c, s, val)
    
    def go_up(et) :
        if et.curr_pos() != et.head_at :
            par_id = et.tree.parentleaf()
            et.set_curr_pos(par_id)
        else :
            et.et_error('go_up', 'Already at head', 1)

    def add_entry(et, item_name, pr, ps, cr=1) :
        et.tree.add(et.curr_pos(), item_name, [
            (et.price, str(pr)),
            (et.pay_source, str(ps)),
            (et.conv_rate, str(cr))
            ]
            )

    def choose_entry(et, prompt, default) :
        # Traverse the tree and choose without changing curr_id. This is for
        # choosing say payment source.
        save_cid = et.curr_pos()
        et.set_curr_pos(et.head_at)
        cont_sel = True
        prefix = 'o'
        prelist = []
        dirlist = []
        width = et.scr.w - 5
        while cont_sel :
            kd, _ = et.current_list()
            choice_lst = []
            for i in kd :
                itm = et.item_at_id(i)
                stritm = (prefix + ' ' + itm)[-width:]
                choice_lst.append(stritm)
            et.lscr.lst = choice_lst
            et.lscr.title = et.item()
            c, s = et.lscr.list_interact(prompt)
            if c == 'selected' :
                sel_val = kd[s]
                if et.is_id_leaf(sel_val) :
                    choice = sel_val
                    cont_sel = False
                else :
                    prelist.append(prefix)
                    dirlist.append(et.curr_pos())
                    prefix = prefix + ' ' + et.item_at_id(sel_val)
                    et.set_curr_pos(sel_val)
            elif c == 'u' :
                if len(prelist) == 0 :
                    et.et_error('choose_entry', 'Already at head', 1)
                else :
                    prefix = prelist.pop()
                    new_id = dirlist.pop()
                    et.set_curr_pos(new_id)
            elif c == 'q' :
                choice = default
                cont_sel = False
            elif c == 'EmptyList' :
                choice = et.et_error('choose_entry',
                        'Cannot choose from empty list. Choice > ', 1)
                cont_sel = False
            else :
                et.et_error('choose_entry', 'Ignoring unknown command:' + c,
                        1)

        et.set_curr_pos(save_cid)
        return choice

    def is_source(et, i) :
        cur_id = et.curr_pos()
        et.set_curr_pos(i)
        _, s = et.current_list()
        # print('is_source', s)
        ret_val = (len(s) != 0)
        et.set_curr_pos(cur_id)
        return ret_val

    def del_entry(et, id) :
        if et.is_id_leaf(id) :
            if et.is_source(id) :
                force = et.et_error('del_entry',
                        'Attempt to delete a source.', 1)
                if force == 'YES' :
                    et.tree.rmlf(id)
            else :
                et.tree.rmlf(id)
        else :
            force = et.et_error('del_entry',
                    'Attempt to delete node.', 1)
            if force == 'YES' :
                et.tree.rmlf(id)

    def edit_item_name_at_id(et, i, name) :
        et.tree.mod_name_at_id(i, name)

    def edit_item_name(et, name) :
        et.tree.mod_name(name)

    def edit_price(et, i, new_p) :
        et.tree.mod_property_at_id(i, et.price, str(new_p))

    def edit_pay_source(et, id, pay_src_id) :
        et.tree.mod_property_at_id(id, et.pay_source, str(pay_src_id))

    def edit_conv_rate(et, id, new_rate) :
        et.tree.mod_property_at_id(id, et.conv_rate, str(new_rate))

    def __str__(et) :
        return et.tree.__str__()

    def __repr__(et) :
        return et.tree.__repr__()

if __name__ == '__main__' :
    import random

    save_file = 'save_expt.txt'

    def rand_str() :
        n = random.randint(4,15)
        rands = ""
        for _ in range(n) :
            rands = rands + random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return rands

    s = screen.Screen(20, 50)
    myet = ExpTree(s)

    myet.safe_loader(save_file)
    print('head:', myet.head_at, ', settings:',  myet.settings_at)

    myet.set_curr_pos(4)
    print(myet.current_list())
    print("Position: ", myet.item())
    for s in myet.print_current_list(40) :
        print(s)

    myet.set_curr_pos(5)
    print("Position: ", myet.item())
    print(myet.current_list())
    for s in myet.print_current_list(40) :
        print(s)

    myet.set_curr_pos(4)

    print("+"*40)
    c, s, v = myet.choose_item()
    if v != -1 :
        print(myet.item_at_id(v))
        myet.edit_item_name_at_id(v, str(random.random()))
        print(myet.item_at_id(v))
    print(c, s)
    print("+"*40)
    myet.add_entry(rand_str(), random.uniform(0,1000), 5, 1)
    myet.add_entry(rand_str(), random.uniform(0,1000), 5, 1)

    print(myet)
    for _ in range(3) :
        myet.go_up()
        print(myet.item(), ": ")
        for s in myet.print_current_list(40) :
            print(s, myet.curr_pos(), myet.head_at)
        print("="*10)

    N = len(myet.tree.t)

    
    if N > 20 :
        print(40*'=')
        print("NUKING")
        print(40*'=')
        for k in range(N) :
            j = random.randint(0, N-1-k)
            id_at_j = myet.tree.t[j][0]
            print("Removing id", id_at_j, myet.item_at_id(id_at_j))
            myet.del_entry(id_at_j)
            myet.save_to_file(save_file)

    print(myet)

    print("Pos. before choice", myet.curr_pos())
    chosen_id = myet.choose_entry('Test choose_entry> ', 0)
    print("Id chosen: " +  myet.item_at_id(chosen_id))
    print("Pos.  after choice", myet.curr_pos())
    updated_price = float(input("Update price to: "))
    myet.edit_price(chosen_id, updated_price)
    updated_pay_source = myet.choose_entry('New pay source> ', 5)
    myet.edit_pay_source(chosen_id, updated_pay_source)
    myet.edit_conv_rate(chosen_id, 10 + 40 * random.random())

    print(myet)

    myet.save_to_file(save_file)


