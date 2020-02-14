#!/usr/bin/python3

import screen

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
    def __init__(self, cms = []) :
        scr = screen.Screen()
        cmds_list = cms + [
                ('n', 'next'),
                ('p', 'prev'),
                ('o', 'other cmds')
                ]
        cmds = dict(cmds_list)

    def list_error(scr, fnname, errname, sev) :
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
        else :
            err_type = 'Warn'
            user_input = scr.scr_error(errname, fnname, 'list_scr', err_type)
        return user_input

    def trim_list(scr, footsize, headsize, l) :
        """
            Returns a list of list of strings made from a list of strings l
            with added item number.
            scr - screen in which the list is to be displayed
            footsize - number of rows occupied by the footer function
            headsize - number of rows occupied by the header function
        """
        ret_list = []
        ht = scr.h
        wd = scr.w

        max_id = len(l)
        len_max_id = 0
        while max_id > 0 :
            len_max_id += 1
            max_id = max_id // 10

        available_wd = wd - len_max_id - 2
        available_ht = ht - footsize - headsize

        if available_ht < min_main_screen_height or available_wd <= 3:
            list_error(scr, 'trim_list', 'Window too small', 2)
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

    def create_header(scr, title, subtitle = "", info = "") :
        scr_wd = scr.w

        head_win = scr.define_win(0, 0, 2, scr_wd)
        scr.win_clear(head_win)
        linf = len(info)
        start_pt = max(scr_wd - linf, 0)
        scr.win_prst(head_win, 0, start_pt, info, min(linf, scr_wd))
        scr.win_center_prst(head_win, 0, title)
        scr.win_center_prst(head_win, 1, subtitle)
        return scr
    # ==Continue==


if __name__ == '__main__' :
    lscr = ListScr(4, 6)
    my_l1 = list(range(999999, 1000016))
    my_l = []
    for x in my_l1 :
        my_l.append(str(x))
    my_l = ['      a'] + my_l
    trimmed_list = trim_list(scr, 2, 2, my_l)
    for l in trimmed_list :
        for a in l :
            print(a)
        print(10*'-')
    scr = create_header(scr, "Expend", "daily", "2/3")
    scr.display()
