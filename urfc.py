#!/usr/bin/python

#URCL flow compiler v0.2022.03

import sys


#io files

infile  = open(sys.argv[1], "r" )
outfile = open(sys.argv[2], "w" )


#global state

urf_label_num = 0

scope_dict_stack = [{}]

#pyblock handler

def pyblock_macro_handler(x):

    exec(txt_block_parser()[0])


#if/else handler

jmp_istr_table = {
    "z"  : "bnz",
    "nz" : "brz",
    "le" : "brg",
    "ge" : "brl",
    "g"  : "ble",
    "l"  : "bge"
}

def if_macro_handler(x):

    global urf_label_num

    x = x[0].split()

    if( x[0] in jmp_istr_table and x[-1] == '{' ):
        local_urf_label_num = urf_label_num
        urf_label_num += 1
        istr_ops = x[1] + ( ' ' + x[2] if x[2] !=  '{' else '' )
        print(jmp_istr_table[x[0]]+' ._urf'+str(local_urf_label_num)+'_else'+' '+istr_ops, file=outfile )
        adj_macro = main_parser()
        #print(adj_macro) 
        if(adj_macro[0] == 'else' and adj_macro[1] == '{' ):
            print('jmp ._urf'+str(local_urf_label_num), file=outfile )
            print('._urf'+str(local_urf_label_num)+'_else', file=outfile )
            main_parser()
        else:
            print('._urf'+str(local_urf_label_num)+'_else', file=outfile )

        print('._urf'+str(local_urf_label_num), file=outfile )


#loop, while, for handlers 

def loop_macro_handler(x):

    global urf_label_num

    x = x[0].split()

    if( x[0] == '{' ):
        local_urf_label_num = urf_label_num
        urf_label_num += 1 
        print('._urf'+str(local_urf_label_num), file=outfile )
        main_parser()
        print('jmp ._urf'+str(local_urf_label_num), file=outfile )        

#func handler

def func_macro_handler(x):
    x = x[0].split()
    #print(x)
    print('.'+x[0]+'\npsh r1\nmov r1 sp \nsub sp sp '+x[1], file=outfile )
    scope_dict_stack.append({})
    main_parser()
    scope_dict_stack.pop()
    print('mov sp r1\npop r1\nret', file=outfile )

#loc variable handler

def nameloc_handler(x):
    x = x[0].split()
    scope_dict_stack[-1][x[0]] = x[1]

def getloc_handler(x):
    x = x[0].split()
    print('sub r1 r1 '+scope_dict_stack[-1][x[1]] + '\nlod '+ x[0] + ' r1\nadd r1 r1 '+ scope_dict_stack[-1][x[1]], file=outfile )

def setloc_handler(x):
    x = x[0].split()
    print('sub r1 r1 '+scope_dict_stack[-1][x[0]] + '\nstr r1 '+ x[1] + '\nadd r1 r1 '+ scope_dict_stack[-1][x[0]], file=outfile )

#main (non ajd) macros dictionary

macros = {
    "{" : pyblock_macro_handler,
    "if" : if_macro_handler,
    "loop" : loop_macro_handler,
    "func" : func_macro_handler,
    "nameloc" : nameloc_handler,
    "getloc" : getloc_handler,
    "setloc" : setloc_handler
}


#main parser

def main_parser():

    adj_macro = None

    for line in infile:

        if line.strip()[0:2] == "@}":
            adj_macro = line.strip()[2:].split(' ', 1 )
            break 

        elif line.strip()[0:1] == "@":
            line = line.strip()[1:].split(' ', 1 )
            macros[line[0]](line[1:])

        elif line.strip() != '':
            print(line, file=outfile )

    return adj_macro


#txt block (no nested macros) parser

def txt_block_parser():

    txt = ""
    adj_macro = None

    for line in infile:
        if line.strip()[0:2] == "@}":
            adj_macro = line.strip()[2:].split(' ', 1 )
            break
        else:
            txt += line
    
    return (txt, adj_macro )


#call main parser

main_parser()