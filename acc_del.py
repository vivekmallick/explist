#!/usr/bin/python3

import exptree
import screen

def accounts(et) :
    cp = et.curr_pos()
    et.set_curr_pos(et.head_at)
    level_lists = []
    level_pos = []
    level_sum = []
    level_lencl1 = []
    cl1, cl2 = et.current_list()
    cl = cl1 + cl2
    lencl1 = len(cl1)
    pos = 0
    sm = 0
    summing = True
    while summing :
        if pos >= len(cl) :
            if len(level_sum) == 0 :
                summing = False
            else : 
                cl = level_lists.pop() 
                pos = level_pos.pop() 
                lencl1 = level_lencl1.pop()
                et.tree.add_or_mod_property_at_id(cl[pos], et.price, str(sm)) 
                sm_old = sm 
                sm = level_sum.pop() 
                if pos < lencl1 :
                    sm += sm_old 
                pos += 1
        else : 
            if et.is_id_leaf(cl[pos]) and (not et.is_source(cl[pos])) : 
                if pos < lencl1 :
                    sm += et.price_of_id(cl[pos]) * et.conv_rate_of_id(cl[pos])
                else :
                    sm -= et.price_of_id(cl[pos]) * et.conv_rate_of_id(cl[pos])
                pos += 1 
            else : 
                level_lists.append(cl) 
                level_pos.append(pos) 
                level_lencl1.append(lencl1)
                level_sum.append(sm) 
                et.set_curr_pos(cl[pos]) 
                cl1, cl2 = et.current_list() 
                cl = cl1 + cl2 
                lencl1 = len(cl1)
                pos = 0 
                sm = 0
       
    et.set_curr_pos(cp)

def del_subtree(et, i) :
    cp = et.curr_pos()
    et.set_curr_pos(i)
    path_stack = []
    deleting = True
    while deleting :
        p = et.curr_pos()
        print("Processing item", p, ':', et.item())
        if et.is_id_leaf(p) and (not et.is_source(p)) :
            print("Deleting item", p, ":", et.item())
            et.del_entry(p)
            if len(path_stack) == 0 :
                deleting = False
            else :
                p = path_stack.pop()
                et.set_curr_pos(p)
        elif not et.is_source(p) :
            path_stack.append(p)
            k, _ = et.current_list()
            et.set_curr_pos(k[0])
        else :
            print('Item: ', et.item(), 'is a source. Not deleting.')
            deleting = False
    et.set_curr_pos(cp)

if __name__ == '__main__' :
    s = screen.Screen()
    et = exptree.ExpTree(s)
    fname = 'acd.txt'
    et.safe_loader(fname)
    accounts(et)
    et.save_to_file(fname)
    del_subtree(et, 4)
    print(et.tree)
