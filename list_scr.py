#!/usr/bin/python3

import screen
import sys
import math

min_main_screen_height = 5

def truncate_str(s, lth) :
    """
        Inputs a string s and a positive integer lth
        and truncates the string to length lth if it is
        longer.
    """
    my_s = s
    if len(s) > lth :
        my_s = s[:lth-1] + '+'
    return my_s

class ListScr :
    def __init__(lscr, scr, cms = [], lst=[]) :
        lscr.scr = scr
        lscr.curr_page = 0
        lscr.cmds_list = cms + [
                ('n', 'next'),
                ('p', 'prev'),
                ('o', 'other cmds')
                ]
        lscr.cmds = dict(lscr.cmds_list)
        lscr.lst = lst
        lscr.page = 0
        lscr.footsize = 2
        lscr.headsize = 2
        lscr.title = ""
        lscr.subtitle = ""
        lscr.head_info = ""
        lscr.footer_pos = 0

    def list_error(lscr, fnname, errname, sev) :
        """
            Error function for list_scr. Entries
            scr: screen
            fnname: function name
            errname: description of the error
            sev: severity - 0 = Debug, 1 = Info, 2 and above = Warning
        """
        if sev == 0 :
            err_type = 'Debug'
        elif sev == 1 :
            err_type = 'Info'
        elif sev == 2 :
            err_type = 'Warn'
        else :
            err_type = 'Critical'
        user_input = lscr.scr.scr_error(errname, fnname, 'list_scr', err_type)
        if sev > 2 :
            sys.exit('list_scr: critical error encountered... exiting.')
        return user_input

    def trim_list(lscr) :
        """
            Returns a list of list of strings made from a list of strings l
            with added item number.
        """
        l = lscr.lst
        ret_list = []
        ht = lscr.scr.h
        wd = lscr.scr.w
        footsize = lscr.footsize
        headsize = lscr.headsize

        max_id = len(l)
        len_max_id = 0
        while max_id > 0 :
            len_max_id += 1
            max_id = max_id // 10

        available_wd = wd - len_max_id - 2
        available_ht = ht - footsize - headsize

        if available_ht < min_main_screen_height or available_wd <= 3:
            lscr.list_error('trim_list', 'Window too small', 2)
        else :
            no_in_page = available_ht - 2
            list_id = 0
            curr_list = []
            for x in l :
                list_id += 1
                str_list_id = " {0:{len_max_id}d} ".format(list_id,
                        len_max_id=len_max_id)
                new_x = str_list_id + truncate_str(x, available_wd)
                curr_list.append(new_x)
                if len(curr_list) == no_in_page :
                    ret_list.append(curr_list)
                    curr_list = []
            if len(curr_list) > 0 :
                ret_list.append(curr_list)
        return ret_list

    def create_header(lscr) :
        scr_wd = lscr.scr.w
        title = lscr.title
        subtitle = lscr.subtitle
        info = lscr.info

        head_win = lscr.scr.define_win(0, 0, 2, scr_wd)
        lscr.scr.win_clear(head_win)
        linf = len(info)
        start_pt = max(scr_wd - linf, 0)
        lscr.scr.win_prst(head_win, 0, start_pt, info, min(linf, scr_wd))
        lscr.scr.win_center_prst(head_win, 0, title)
        lscr.scr.win_center_prst(head_win, 1, subtitle)
        return None

    def create_footer(lscr) :
        scr_wd = lscr.scr.w
        if scr_wd <= 20 :
            lscr.list_error("create_footer", "screen width too small", 3)
        cmdwd = max((scr_wd // 3), 10)
        ntabs = scr_wd // cmdwd
        perpage = 2 * ntabs
        ncmds = len(lscr.cmds_list)
        npages = math.ceil(ncmds / perpage)
        if lscr.footer_pos >= ncmds :
            lscr.list_error("create_footer", "incorrect footer position", 1)
            lscr.footer_pos = 0
        pos = lscr.footer_pos
        lst_to_show = lscr.cmds_list[pos :
                min((pos + perpage), ncmds) ]
        lst_to_show_str = []
        for p in lst_to_show :
            lst_to_show_str.append(p[0] + ':' + p[1])
        lst_to_show_str = lst_to_show_str + (2*ntabs -
                len(lst_to_show_str))*[' ']
        for i in [-2, -1] :
            r = lscr.scr.h + i
            for t in range(ntabs) :
                c = t * cmdwd
                lscr.scr.prst(r, c, lst_to_show_str[(i+2)*ntabs + t], cmdwd)
        return perpage

    def disp_list(lscr) :
        ll = lscr.trim_list()
        if len(ll) > 0 :
            lcurr = ll[lscr.curr_page]
            offset_head = lscr.headsize + 1
            width = lscr.scr.w
            for i in range(len(lcurr)) :
                r = offset_head + i
                c = 0
                lscr.scr.prst(r, c, lcurr[i], width)
        else :
            lscr.list_error('disp_list', 'empty list', 1)
        return None

    def list_interact(lscr, prompt) :
        selection = 0
        stay = True
        lenlist = len(lscr.lst)
        lenopts = len(lscr.cmds_list)
        lscr.curr_page = 0
        if lenlist == 0 :
            cmd = 'EmptyList'
            stay = False
        while stay :
            no_pages = len(lscr.trim_list())
            lscr.info = str(lscr.curr_page + 1) + '/' + str(no_pages)
            lscr.scr.clear()
            lscr.create_header()
            opt_pg = lscr.create_footer()
            lscr.disp_list()
            lscr.scr.display()
            ans = input(prompt)

            if ans == 'n' :
                if lscr.curr_page < no_pages - 1 :
                    lscr.curr_page += 1
            elif ans == 'p' :
                if lscr.curr_page > 0 :
                    lscr.curr_page -= 1
            elif ans == 'o' :
                lscr.footer_pos += opt_pg
                if lscr.footer_pos >= lenopts :
                    lscr.footer_pos = 0
            elif ans.isnumeric() :
                chosen = int(ans) - 1
                if chosen < 0 or chosen >= lenlist :
                    lscr.list_error("list_interact",
                            "Invalid choice. Please select again.", 1)
                else :
                    selection = chosen
                    cmd = "selected"
                    stay = False
            else :
                cmd = ans
                stay = False
        return (cmd, selection)

if __name__ == '__main__' :
    s = screen.Screen(15, 40)
    lscr = ListScr(s)
    lscr.scr.h = 20
    lscr.scr.w = 45
    lscr.scr.setscreen()
    lscr.title = "Expenditure"
    lscr.subtitle = "daily"
    lscr.info = "2/3"
    lscr.cmds_list.append(('d', 'delete'))
    lscr.cmds_list.append(('a', 'add'))
    lscr.cmds_list.append(('c', 'compute'))
    lscr.cmds_list.append(('s', 'select'))
    my_l1 = list(range(999999, 1000116))
    my_l = []
    for x in my_l1 :
        my_l.append(str(x))
    lscr.lst = my_l
    lscr.create_header()
    lscr.create_footer()
    lscr.scr.display()
    lscr.disp_list()
    lscr.scr.display()
    c, s = lscr.list_interact('LSCR> ')
    if c == "selected" :
        print(lscr.lst[s], s)
    else :
        print(c, s)
