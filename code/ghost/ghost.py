#!/usr/bin/env python

import re
import sys
import os.path

class ParseError(Exception):
    pass

COMMAND = r'[a-zA-Z]+'
REGISTER_ARG = r'[a-hA-H]|(pc)|(PC)'
INDIRECT_ARG = r'\[[a-hA-H]\]'
MEMORY_ARG = r'\[\d+\]'
CONSTANT_ARG = r'\d+'
LABEL_ARG = r'#[_a-z][_a-z0-9]*'
LABEL = r'[_a-z][_a-z0-9]*:'
COMMENT = r';.*'

ARG = r'(%s)|(%s)|(%s)|(%s)|(%s)' % (REGISTER_ARG, INDIRECT_ARG, MEMORY_ARG, CONSTANT_ARG, LABEL_ARG)
ARGS = r'(%s)(\s*,\s*(%s)){0,2}' % (ARG, ARG)

COMMAND_LINE = r'\s*(%s)(\s+(%s))?\s*(%s)?$' % (COMMAND, ARGS, COMMENT)
LABEL_LINE = r'\s*(%s)\s*(%s)?$' % (LABEL, COMMENT)
EMPTY_LINE = r'\s*(%s)?$' % COMMENT

def parse_file(f):
    cmds = []
    labels = {}
    for line_nbr, line in enumerate(f):
        try:
            parsed_line = parse_line(line)
            line_type = parsed_line[0]
            if line_type == 'COMMAND':
                cmds.append(parsed_line)
            elif line_type == 'LABEL':
                label = parsed_line[1]
                if label in labels:
                    print 'Error: Reused label (%s) at line %d.' % (label, line_nbr)
                    sys.exit(1)
                labels[label] = len(cmds)
        except ParseError as error:
            print 'Error: Failed to parse line %d:' % line_nbr
            print line
            sys.exit(1)
    return cmds, labels

def parse_line(line):
    m = re.match(COMMAND_LINE, line)
    if m:
        return parse_command(m)
    m = re.match(LABEL_LINE, line)
    if m:
        return parse_label(m)
    m = re.match(EMPTY_LINE, line)
    if m:
        return 'EMPTY',
    raise ParseError('Invalid line: %s' % line)

def parse_command(match):
    command = match.group(1).upper()
    args = parse_args(match.group(2))
    return 'COMMAND', command, args

def parse_args(arg_str):
    args = []
    if arg_str is not None:
        args = [parse_arg(arg) for arg in arg_str.split(',')]
    return tuple(args)

def parse_arg(arg_str):
    arg_str = arg_str.strip()
    m = re.match(LABEL_ARG, arg_str)
    if m:
        return 'LABEL', m.group(0)[1:]
    return 'ARG', arg_str

def parse_label(match):
    label = match.group(1)[:-1]
    return 'LABEL', label

def generate_code(cmds, labels):
    code = []
    for cmd in cmds:
        args = []
        for arg in cmd[2]:
            if arg[0] == 'LABEL':
                args.append(str(labels[arg[1]]))
            else:
                args.append(arg[1])
        code.append('%s %s' % (cmd[1], ','.join(args)))
    return '\n'.join(code)
    
if __name__ == '__main__':
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as f:
            cmds, labels = parse_file(f)
            print generate_code(cmds, labels)
    else:
        print 'usage: %s input_file' % os.path.basename(sys.argv[0])
