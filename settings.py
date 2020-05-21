import exptree
import screen
import list_scr

class Settings :
    def __init__(sts, exptree, scr) :
        sts.valstr = 'val'

        sts.set_dict = {
                'win_height': 15,
                'win_width': 40,
                'def_pay_src': 3,
                'start_pos': 2,
                'def_conv': 10000
                }
        sts.pay_src_dict = {}

        sts.et = exptree
        sts.s = scr

        sts.allowed_keys = sts.set_dict.keys()

    def error(sts, fname, err_str, err_type) :
        if err_type == 0 :
            err = 'debug'
        elif err_type == 1 :
            err = 'info'
        elif err_type == 2 :
            err = 'Warn'
        else :
            err = 'Critical'

        sts.s.scr_error(err_str, fname, 'settings', err)

    def read_exptree(sts) :
        et = sts.et
        settings = et.settings_at
        cp = et.curr_pos()
        et.set_curr_pos(settings)
        set_ids, _ = et.current_list()
        list_sets = []
        for sid in set_ids :
            prop = et.item_at_id(sid)
            val = et.tree.value_property_at_id(sid, sts.valstr)
            list_sets.append((prop, int(val)))
        sts_dict = dict(list_sets)
        for ky in sts.allowed_keys :
            if ky in sts_dict.keys() :
                sts.set_dict[ky] = sts_dict[ky]
        if 'pay_src_dict' in sts_dict.keys() :
            psd_id = -1
            l = 0
            finding_psd = True
            while finding_psd :
                if list_sets[l][0] == 'pay_src_dict' :
                    finding_psd = False
                    psd_id = set_ids[l]
                else :
                    l += 1

            if psd_id == -1 :
                sts.error('read_exptree', 'should not reach here.', '3')
            else :
                et.set_curr_pos(psd_id)
                list_abrvs = []
                abrv_ids, _ = et.current_list()
                print(abrv_ids)
                for a in abrv_ids :
                    abrv = et.item_at_id(a)
                    psrcid = et.tree.value_property_at_id(a, sts.valstr)
                    list_abrvs.append((abrv, int(psrcid)))
                sts.pay_src_dict.update(list_abrvs)
        et.set_curr_pos(cp)

    def print_settings(sts) :
        print(sts.set_dict)
        print(sts.pay_src_dict)

    def clear_settings(sts) :
        et = sts.et
        settings = et.settings_at
        cp = et.curr_pos()
        stack = []
        cleared = False
        p = settings
        while not cleared :
            if len(stack) == 0 and et.is_id_leaf(p) :
                cleared = True
            elif et.is_id_leaf(p) :
                et.del_entry(p)
                p = stack.pop()
            else :
                stack.append(p)
                et.set_curr_pos(p)
                lvs, _ = et.current_list()
                p = lvs[0]
        et.set_curr_pos(cp)

    def save_settings_pre(sts) :
        et = sts.et
        for ky in sts.set_dict.keys() :
            et.tree.add(sts.et.settings_at, ky, [(sts.valstr,
                str(sts.set_dict[ky]))])
        if len(sts.pay_src_dict) != 0 :
            psd = et.tree.add(sts.et.settings_at, 'pay_src_dict',
                    [(sts.valstr, '0')])
            for ky in sts.pay_src_dict.keys() :
                et.tree.add(psd, ky, [(sts.valstr,
                    str(sts.pay_src_dict[ky]))])
        return None

    def modify_height(sts) :
        s = sts.s
        a = s.scr_input(
        'Input + to increase height and - to reduce. Press q to stop.',
        'ht (+/-/q) > '
        )
        while a != 'q' :
            if a == '+' :
                s.incr_ht()
            elif a == '-' :
                s.decr_ht()
            else :
                sts.error('modify_height', 'please enter +/-/q', 1)
            a = s.scr_input(
            'Input + to increase height and - to reduce. Press q to stop.',
            'ht (+/-/q) > '
            )
            
        sts.set_dict['win_height'] = s.h

    def modify_width(sts) :
        s = sts.s
        a = s.scr_input(
        'Input + to increase width and - to reduce. Press q to stop.',
        'wd (+/-/q) > '
        )
        while a != 'q' :
            if a == '+' :
                s.incr_wd()
            elif a == '-' :
                s.decr_wd()
            else :
                sts.error('modify_width', 'please enter +/-/q', 1)
            a = s.scr_input(
            'Input + to increase width and - to reduce. Press q to stop.',
            'wd (+/-/q) > '
            )
            
        sts.set_dict['win_width'] = s.w

    def mod_default_source(sts) :
        c = sts.et.choose_entry('default source > ',
        sts.set_dict['def_pay_src'])
        sts.set_dict['def_pay_src'] = c

    def mod_start_pos(sts) :
        c = sts.et.choose_entry('default start page > ', 2)
        sts.set_dict['start_pos'] = c

    def mod_conv_rate(sts) :
        cr = sts.s.scr_input('New conversion rate?', 'conv_rate > ')
        sts.set_dict['def_conv'] = int(10000 * float(cr))

    def add_mod_abbrv(sts) :
        ab = sts.s.scr_input('Abbreviation', 'ab > ')
        abid = sts.et.choose_entry('pay_source > ',
        sts.set_dict['def_pay_src'])
        sts.pay_src_dict.update([(ab, abid)])

    def save_settings(sts) :
        sts.clear_settings()
        sts.save_settings_pre()

    def print_abbr(sts) :
        if len(sts.pay_src_dict) == 0 :
            sts.s.scr_input('No abbreviations defined yet.',
            'Settings (press enter)')
        else :
            l = list_scr.ListScr(sts.s, [('q', 'quit')])
            l.lst = []
            for k in sts.pay_src_dict.keys() :
                v = sts.pay_src_dict[k]
                it = sts.et.item_at_id(int(v))
                w = sts.s.w
                l.lst.append(k + ': ' + it)
            c, s = l.list_interact('Settings abbrv> ')
            if c == 'selected' :
                k = list((sts.pay_src_dict.keys()))[s]
                del sts.pay_src_dict[k]
                            
if __name__ == '__main__' :
    screen = screen.Screen(20, 60)
    expend = exptree.ExpTree(screen)
    sts_test_file = 'settings_test.txt'
    expend.safe_loader(sts_test_file)
    sets = Settings(expend, screen)
    sets.print_settings()
    sets.read_exptree()
    sets.print_settings()
    sets.modify_height()
    sets.modify_width()
    sets.mod_default_source()
    sets.add_mod_abbrv()
    sets.print_settings()
    sets.print_abbr()
    sets.clear_settings()
    sets.save_settings_pre()
    expend.save_to_file(sts_test_file)
