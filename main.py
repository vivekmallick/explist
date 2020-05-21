import exptree
import screen
import settings
import sys
import acc_del

def explist_err(s, func_name, err_desc, sev) :
    if sev == 0 :
        err_type = 'Debug'
    elif sev == 1 :
        err_type = 'Info'
    elif sev == 2 :
        err_type = 'Warn'
    else :
        err_type = 'Critical'

    ui = s.scr_error(err_desc, func_name, 'explist', err_type)
    if sev > 2 :
        sys.exit('explist: crash induced by non-recoverable error.')
    return ui

def fill_form(et, form_string) :
    ansdict = {}
    lstr = len(form_string)
    upd_string = ""
    pos = 0
    state = 0 # 0 -- normal, 1 -- found first _, 2 -- _? reaidng var
              # 3 -- _?*? waiting for _, -> 0
    curr_var = ""
    not_OK = True
    while not_OK :
        for c in form_string:
            if c == '_' :
                if state == 0 :
                    state = 1
                elif state == 1 :
                    upd_string = upd_string + '__'
                    state = 0
                elif state == 2 :
                    explist_err(et.scr, 'fill_form',
                            'Character _ is not allowed in variable name', 3)
                elif state == 3 :
                    state = 0
                    curr_val = et.scr.scr_input(upd_string, curr_var + '> ')
                    ansdict.update([(curr_var, curr_val)])
                    upd_string = upd_string + ' ' + curr_val + ' '
                    curr_var = ""
                else :
                    explist_err(et.scr, 'fill_form',
                            'Error triggered by some bug', 3)
            elif c == '?' :
                if state == 0 :
                    upd_string = upd_string + '?'
                    state = 0
                elif state == 1 :
                    state = 2
                elif state == 2 :
                    state = 3
                elif state == 3 :
                    explist_err(et.scr, 'fill_form',
                            'Character ? is not allowed in variable name', 3)
                else :
                    explist_err(et.scr, 'fill_format',
                            'Error triggered by some bug', 3)
            elif c == '\n' :
                upd_string = upd_string + ' '
            else :
                if state == 0 :
                    upd_string = upd_string + c
                    state = 0
                elif state == 1 :
                    upd_string = upd_string + '_' + c
                    state = 0
                elif state == 2 :
                    curr_var = curr_var + c
                elif state == 3 :
                    explist_err(et.scr, 'fill_form',
                            'Character ? is not allowed in variable name', 3)
                else :
                    explist_err(et.scr, 'fill_format',
                            'Error triggered by some bug', 3)
        is_OK = et.scr.scr_input(upd_string, 'OK? (Y/n) ')
        if is_OK != 'n' and is_OK != 'N' :
            not_OK = False
        upd_string = ""
    return ansdict

def safe_float(s) :
    try :
        i = float(s)
    except ValueError :
        i = None
    return i

def proc_vague_cmd(el, c) :
    et = el.expt
    cr = float(el.sts.set_dict['def_conv']) / 10000.0
    dps = el.sts.set_dict['def_pay_src']
    print("Trying to interpret the command: " + c)
    first_split = c.split(';')
    processing_failed = False
    if len(first_split) == 2 :
        paysrc_ab = first_split[1].strip()
        try : 
            paysrc = el.sts.pay_src_dict[paysrc_ab]
        except KeyError :
            processing_failed = True
    elif len(first_split) == 1 :
        paysrc = dps
    else :
        processing_failed = True

    if not processing_failed : 
        second_split = first_split[0].split(' ') 
        pos_price = second_split[-1] 
        rest = second_split[:-1] 
        price = safe_float(pos_price) 
        if price == None : 
            item_name = ' '.join(second_split) 
            ans = fill_form(et, 'Item: ' + item_name + ', price: _?price?_') 
            p = ans['price'] 
            pr = safe_float(p) 
            if pr == None : 
                processing_failed = True 
            else : 
                et.add_entry(item_name, pr, paysrc, cr) 
        else : 
            item_name = ' '.join(rest) 
            et.add_entry(item_name, price, paysrc, cr)

    if processing_failed :
        explist_err(el.s, 'proc_vague_cmd', 'Command ' + c + ' could not be understood.', 1)

def proc_acc_cmd(el, c) :
    et = el.expt
    print("Processing accounts cmd: " + c)
    if c == 'A' :
        acc_del.accounts(et)
    elif c == 'D' :
        p = et.curr_pos()
        et.go_up()
        p_name = et.item_at_id(p)
        ans = fill_form(et,
                'The current entry ' +  p_name + ' id: ' + str(p) +
                ' and all sub-entries will be deleted. OK?  _?ok?_'
                )
        if ans['ok'] == 'y' or ans['ok'] == 'Y' :
            acc_del.del_subtree(et, p)
    else :
        proc_vague_cmd(el, c)

def proc_settings_cmd(el, c) :
    print('Processing settings cmd: ' + c)
    if c == 'sh' :
        el.sts.modify_height()
    elif c == 'sw' :
        el.sts.modify_width()
    elif c == 'sp' :
        el.sts.mod_default_source()
    elif c == 'sa' :
        el.sts.add_mod_abbrv()
    elif c == 'ss' :
        el.sts.mod_start_pos()
    elif c == 'sc' :
        el.sts.mod_conv_rate()
    elif c == 'sdl' :
        el.sts.print_abbr()
    else : 
        proc_acc_cmd(el, c)
    el.sts.save_settings()

def proc_mod_cmd(el, c) :
    et = el.expt
    print("processing mod command: ", c)
    if c == 'p' :
        old_price = et.price_at_pos()
        np_dict = fill_form(et, 'Old price: ' + str(old_price)
                + ', new price: _?prc?_')
        np = float(np_dict['prc'])
        et.edit_price(et.curr_pos(), np)
    elif c == 'c' :
        cv_dict = fill_form(et, 'New conversion rate: _?convrate?_')
        cvr = float(cv_dict['convrate'])
        et.edit_conv_rate(et.curr_pos(), cvr)
    elif c == 'N' :
        nm_dict = fill_form(et, 'Change name from ' + et.item()
                + ' to _?newname?_')
        newnm = nm_dict['newname']
        et.edit_item_name(newnm)
    elif c == 's' :
        new_src = et.choose_entry('New payment source > ', 3)
        et.edit_pay_source(et.curr_pos(), new_src)
    else :
        proc_settings_cmd(el, c)


def process_cmd(el, c) :
    et = el.expt
    print("processing command: ", c)
    if c == 'u' :
        et.go_up()
    elif c == 'a' :
        add_data = fill_form(et, 
                '''
Item_name: _?itemname?_,
Price    : _?price?_,
Conv     : _?conv?_.
                ''')
        item = add_data['itemname']
        price = float(add_data['price'])
        cvrate = float(add_data['conv'])
        pay_src = et.choose_entry('payment source > ', 3)
        et.add_entry(item, price, pay_src, cvrate)
    elif c == 'd' :
        dcp = et.curr_pos()
        et.go_up()
        et.del_entry(dcp)
    elif c == 'l' :
        wd = et.scr.w
        prin_l = et.print_current_list(wd - 10)
        et.lscr.lst = prin_l
        c, s = et.lscr.list_interact('Listing > ')
        if c == "selected" :
            explist_err(et.scr, 'process_cmd', 'l is only for listing.', 1)
    elif c == 'q' :
        explist_err(et.scr, 'process_cmd', 'Maybe try "exit"', 1)
    else :
        proc_mod_cmd(el, c)

def expt_interact(el) :
    et = el.expt
    prompt = el.prompt
    cont_interaction = True
    cmd_issued = False
    v = el.start_pos
    while cont_interaction :
        if et.is_id_leaf(v) :
            c = et.show_leaf_at_id(v, prompt)
        else :
            v_old = v
            c, s, v = et.choose_item(prompt)
        if c == 'selected' :
            et.set_curr_pos(v)
        elif c == 'EmptyList' :
            v = v_old
            et.set_curr_pos(v)
            cmd = et.show_leaf_at_id(v, prompt)
            cmd_issued= True
        elif c == 'S' :
            et.save_to_file(el.el_file)
            v = et.curr_pos()
        elif c == 'exit' :
            cont_interaction = False
        else :
            process_cmd(el, c)
            v = et.curr_pos()


class ExpList () :
    def __init__(el) :
        el.prompt = 'ExpList> '
        el.s = screen.Screen(h=15, w=40)
        el.expt = exptree.ExpTree(el.s, cmds=[
            ('a', 'add'),
            ('d', 'delete'),
            ('p', 'modprice'),
            ('l', 'list'),
            ('c', 'conv-rate'),
            ('N', 'ch name'),
            ('s', 'ch src'),
            ('S', 'save'),
            ('sh', 'mod win ht'),
            ('sw', 'mod win wd'),
            ('sp', 'mod def pay'),
            ('sa', 'add pay abr'),
            ('ss', 'mod start page'),
            ('sc', 'mod conv rate'),
            ('sdl', 'vw/del ab'),
            ('A', 'accounts'),
            ('D', 'delete subtree')
            ])
        el.el_file = 'save_expt.txt'
        el.expt.safe_loader(el.el_file)

        el.sts = settings.Settings(el.expt, el.s)
        el.sts.read_exptree()
        el.s.h = el.sts.set_dict['win_height']
        el.s.w = el.sts.set_dict['win_width']
        el.s.setscreen()
        el.s.display()
        el.def_src = el.sts.set_dict['def_pay_src']
        el.start_pos = el.sts.set_dict['start_pos']

    def explist_interact(el) :
        el.expt.set_curr_pos(el.start_pos)
        expt_interact(el)
        el.expt.save_to_file(el.el_file)


if __name__ == '__main__' :
    explst = ExpList()
    explst.explist_interact()
