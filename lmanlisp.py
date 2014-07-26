# -*- coding: utf-8 -*-
#
# This is adapted from Peter Norvig's minimal lisp:
#
# http://norvig.com/lispy.html
#
# And from this:
#
# http://carlo-hamalainen.net/stuff/bfpg-mini-lisp/slides-2013-05-28.pdf
# https://github.com/carlohamalainen/pysecd

import re
import sys
import uuid

Symbol = str
isa = isinstance

def index(e, n):
    """
    Basically looks up which frame that is allocated for this identifier (I think)
    """
    def indx2(e, n, j):
        if len(n) == 0:
            return []
        elif n[0] == e:
            return j
        else:
            return indx2(e, n[1:], j + 1)

    def indx(e, n, i):
        if len(n) == 0:
            return []

        j = indx2(e, n[0], 0)

        if j == []:
            return indx(e, n[1:], i + 1)
        else:
            return [i, j]

    rval = indx(e, n, 0)

    if rval == []:
        return rval
    else:
        assert len(rval) == 2
        assert type(rval[0]) == int
        assert type(rval[1]) == int
        return rval

def is_atom(e):
    return e == "nil" or isa(e, int) or isa(e, Symbol)

def compile_lambda(body, n, c):
    return ["LDF", compile(body, n, []) + ["RTN"]] + c

def compile_if(test, then_code, else_code, n, c):
    then_compiled = compile(then_code, n, [])
    else_compiled = compile(else_code, n, [])
    return compile(test, n, []) + ["SEL"] + [then_compiled + ["JOIN"]] + [else_compiled + ["JOIN"]] + c

def compile_app(args, n, c):
    if args == []:
        return c
    else:
        return compile_app(args[0:-1], n, compile(args[-1], n, c))

def compile_tuple(args, n, c):
    def do_compile_tuple(args, n, calls, c):
        if args == []:
            return c + [["CONS"]] * (calls - 1)
        else:
            return do_compile_tuple(args[0:-1], n, calls + 1, compile(args[-1], n, c))
    return do_compile_tuple(args, n, 0, []) + c

def compile_list(args, n, c):
    # lists are tuples with an extra 0 really
    return compile_tuple(args + [0], n, c)

def compile(e, n, c):
    # print "e:", e
    # print "n:", n
    # print "c:", c
    if isa(e, list) and not e:
        return c

    if is_atom(e):
        if e == "nil":
            # Use 0 for nil
            return ["LDC", "0"] + c
        if isa(e, Symbol):             # variable reference
            ij = index(e, n)
            #print e, n
            assert(ij)
            return ["LD"]  + ij  + ["; %s"%e] + c
        else:         # constant literal
            return ["LDC", str(e)] + c
    else:
        fcn = e[0]
        args = e[1:]
        if is_atom(fcn):
            if fcn == '+' or fcn == 'add':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["ADD"] + compile(e, n, c)
            elif fcn == '-' or fcn == 'sub':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["SUB"] + compile(e, n, c)
            elif fcn == '*' or fcn == 'mul':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["MUL"] + compile(e, n, c)
            elif fcn == '/' or fcn == 'div':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["DIV"] + compile(e, n, c)
            elif fcn == 'eq':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["CEQ"] + compile(e, n, c)
            elif fcn == '>' or fcn == 'gt':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["CGT"] + compile(e, n, c)
            elif fcn == '>=' or fcn == 'geq':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["CGTE"] + compile(e, n, c)
            elif fcn == '<' or fcn == 'lt':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["CGTE", "LDC", 0, "CEQ"] + compile(e, n, c)
            elif fcn == '<=' or fcn == 'leq':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, c) + compile(arg2, n, []) + ["CGT", "LDC", 0, "CEQ"] + compile(e, n, c)
            elif fcn == 'car':
                e.pop(0)
                arg1 = e.pop(0)
                return compile(arg1, n, []) + ["CAR"] + compile(e, n, c)
            elif fcn == 'cdr':
                e.pop(0)
                arg1 = e.pop(0)
                return compile(arg1, n, []) + ["CDR"] + compile(e, n, c)
            elif fcn == 'cons':
                e.pop(0)
                arg1 = e.pop(0)
                arg2 = e.pop(0)
                return compile(arg1, n, []) + compile(arg2, n, []) + ["CONS"] + compile(e, n, c)
            elif fcn == 'atom':
                e.pop(0)
                arg1 = e.pop(0)
                return compile(arg1, n, []) + ["ATOM"] + compile(e, n, c)
            elif fcn == 'lambda':
                args = e[1:]
                assert len(args) == 2 # i.e. args == [name list, body]
                return compile_lambda(args[1], [args[0]] + n, c)
            elif fcn == 'if':
                return compile_if(args[0], args[1], args[2], n, c)
            elif fcn == 'let' or fcn == 'letrec':
                newn = [args[0]] + n
                values = args[1]
                body = args[2]
                if fcn == 'let':
                    return compile_app(values, n, compile_lambda(body, newn, ["AP", len(values)] + c))
                elif fcn == 'letrec':
                    return ["DUM", len(values)] + compile_app(values, newn, compile_lambda(body, newn, ["RAP", len(values)] + c))
            elif fcn == 'list':
                return compile_list(args, n, c)
            elif fcn == 'tuple':
                return compile_tuple(args, n, c)
            elif fcn == 'print':
                thingie = compile(args[0], n, [])
                res = thingie + ["DBUG"] + thingie + c
                return res
            # elif fcn == 'null':
            #     e.pop(0)
            #     arg1 = e.pop(0)
            #     return compile(arg1, n, c) + ["LDC", "0", "CEQ"] + compile(e, n, c)
            else:
                return compile_app(args, n, ["LD"] + index(fcn, n) + ["; %s"%fcn] + ["AP", len(args)] + c)
        else: # an application with nested function
            return compile_app(args, n, compile(fcn, n, ["AP", len(args)] + c))

def make_label():
    return "__label_" + str(uuid.uuid4())

def do_output(program, label):
    o = [label]
    subs = []
    while program:
        if program[0] == "LDF":
            newlabel = make_label()
            subs.append(do_output(program[1], newlabel))
            o.append(["LDF", newlabel])
            program = program[2:]
        elif program[0] == "SEL":
            then_label = make_label()
            else_label = make_label()
            subs.append(do_output(program[1], then_label))
            subs.append(do_output(program[2], else_label))
            o.append(["SEL", then_label, else_label])
            program = program[3:]
        elif program[0] == "LD":
            o.append(["LD", program[1], program[2], program[3]])
            program = program[4:]
        elif program[0] in ["LDC", "AP", "RAP", "DUM"]:
            o.append([program[0], program[1]])
            program = program[2:]
        else:
            o.append(program[0])
            program = program[1:]
    for sub in subs:
        o.extend(sub)
    return o

def output(program):
    o = do_output(program, "")
    tagged = []
    for op in o:
        #print op
        if isa(op, list):
            tagged.append(" ".join([str(x) for x in op]))
        else:
            tagged.append(op)
    return labels_to_linums(tagged)

def labels_to_linums(program):
    ix = 0
    while ix < len(program):
        line = program[ix]
        if line.startswith("__label_"):
            newprogram = []
            for i, l in enumerate(program):
                if i == ix:
                    continue
                newprogram.append(l.replace(line, str(ix)))
            program = newprogram
        elif len(line) == 0:
            program = program[0:ix] + program[ix+1:]
        else:
            ix += 1
    return program

def read(s):
    return read_from(tokenize(s))

parse = read

def tokenize(s):
    "Convert a string into a list of tokens."
    # remove any comments
    s = re.sub(r';.*', '', s)
    # add spaces around all parentheses
    return s.replace('(',' ( ').replace(')',' ) ').split()

def read_from(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Integers become integers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        return Symbol(token)

if __name__=="__main__":
    program = open(sys.argv[1]).read()
    a = parse(program)
    names = []
    c = ["RTN"]
    b = compile(a, names, c)
    o = output(b)
    print "\n".join(o)
