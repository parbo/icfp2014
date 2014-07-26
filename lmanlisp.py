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

import sys

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

def flatten1L(x):
    return [inner for outer in x for inner in outer]

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
            try:
                assert(ij)
            except AssertionError:
                print e, n
                raise
            return ["LD"]  + ij  + c
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
                args = e[1:]
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
                list_body = flatten1L([compile(list_item, n, ["CONS"]) for list_item in args][::-1])
                # int 0 for nil
                return ["LDC", "0"] + list_body + c
            # elif fcn == 'null':
            #     e.pop(0)
            #     arg1 = e.pop(0)
            #     return compile(arg1, n, c) + ["LDC", "0", "CEQ"] + compile(e, n, c)
            else:
                return compile_app(args, n, ["LD"] + index(fcn, n) + ["AP", len(args)] + c)
        else: # an application with nested function
            return compile_app(args, n, compile(fcn, n, ["AP", len(args)] + c))

def do_output(program, subs):
    o = []
    while program:
        if program[0] == "LDF":
            code = do_output(program[1], subs)
            o.append(["LDF", len(subs)])
            subs.append(code)
            program = program[2:]
        elif program[0] == "SEL":
            code = do_output(program[1], subs)
            then_label = len(subs)
            subs.append(code)
            else_label = len(subs)
            code = do_output(program[2], subs)
            subs.append(code)
            o.append(["SEL", then_label, else_label])
            program = program[3:]
        elif program[0] == "LD":
            o.append(["LD", program[1], program[2]])
            program = program[3:]
        elif program[0] in ["LDC", "AP", "RAP", "DUM"]:
            o.append([program[0], program[1]])
            program = program[2:]
        else:
            o.append(program[0])
            program = program[1:]
    return o

def output(program):
    subs = []
    label = 0
    o = do_output(program, subs)
    labels = {}
    pc = len(o)
    for i, s in enumerate(subs):
        labels[i] = pc
        pc += len(s)
        s[0].append("; >> label %d"%i)
        o.extend(s)
    tagged = []
    for line, op in enumerate(o):
        if isa(op, list):
            if op[0] in ["LDF", "SEL"]:
                op_labels = [label for label in op[1:] if not isa(label, str)]
                instructions = [str(labels[label]) for label in op_labels]
                comments = ["label " + str(label) for label in op_labels]
                tagged.append(" ".join([op[0]] + instructions + ["; %d "%line] + comments))
            else:
                tagged.append(" ".join([op[0]] + [str(arg) for arg in op[1:]] + ["; %d"%line]))
        else:
            if line == len(o) - 1:
                tagged.append(op) # no comments on last line?
            else:
                tagged.append(op +  " ; %d"%line)
    return tagged

def read(s):
    return read_from(tokenize(s))

parse = read

def tokenize(s):
    "Convert a string into a list of tokens."
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
    print a
    names = []
    c = ["RTN"]
    b = compile(a, names, c)
    print b
    o = output(b)
    print o
    print "\n".join(o)