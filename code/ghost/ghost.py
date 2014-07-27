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

class Parser(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._lines = []
        self._cmds = []
        self._labels = {}

    def parse_file(self, f):
        self.reset()
        for line_nbr, line in enumerate(f):
            try:
                parsed_line = self.parse_line(line)
                parsed_line['CODE'] = line.rstrip()
                parsed_line['NBR'] = line_nbr
                self._lines.append(parsed_line)
                line_type = parsed_line['TYPE']
                if line_type == 'COMMAND':
                    self._cmds.append(parsed_line)
                elif line_type == 'LABEL':
                    label = parsed_line['LABEL']
                    if label in self._labels:
                        print 'Error: Reused label (%s) at line %d.' % (label, line_nbr)
                        sys.exit(1)
                    self._labels[label] = len(self._cmds)
            except ParseError as error:
                print 'Error: Failed to parse line %d:' % line_nbr
                print line
                sys.exit(1)

    def parse_line(self, line):
        m = re.match(COMMAND_LINE, line)
        if m:
            return self.parse_command(m)
        m = re.match(LABEL_LINE, line)
        if m:
            return self.parse_label(m)
        m = re.match(EMPTY_LINE, line)
        if m:
            return self.parse_empty(m)
        raise ParseError('Invalid line: %s' % line)

    def parse_command(self, match):
        command = match.group(1).upper()
        args = self.parse_args(match.group(2))
        return {'TYPE': 'COMMAND', 'COMMAND': command, 'ARGS': args}

    def parse_args(self, arg_str):
        args = []
        if arg_str is not None:
            args = [self.parse_arg(arg) for arg in arg_str.split(',')]
        return args

    def parse_arg(self, arg_str):
        arg_str = arg_str.strip()
        m = re.match(REGISTER_ARG, arg_str)
        if m:
            register = m.group(0).lower()
            return {'TYPE': 'REGISTER', 'STR': register, 'REGISTER': register}
        m = re.match(INDIRECT_ARG, arg_str)
        if m:
            indirect = m.group(0).lower()
            return {'TYPE': 'INDIRECT', 'STR': indirect, 'REGISTER': indirect[1]}
        m = re.match(MEMORY_ARG, arg_str)
        if m:
            memory = m.group(0)
            address = int(memory[1:-1])
            return {'TYPE': 'MEMORY', 'STR': memory, 'ADDRESS': address}
        m = re.match(CONSTANT_ARG, arg_str)
        if m:
            constant = m.group(0)
            return {'TYPE': 'CONSTANT', 'STR': constant, 'CONSTANT': int(constant)}
        m = re.match(LABEL_ARG, arg_str)
        if m:
            label = m.group(0)[1:]
            return {'TYPE': 'LABEL', 'STR': label, 'LABEL': label}
        raise ParseError('Invalid argument: %s' % arg_str)

    def parse_label(self, match):
        label = match.group(1)[:-1]
        return {'TYPE': 'LABEL', 'LABEL': label}

    def parse_empty(self, match):
        return {'TYPE': 'EMPTY'}

    def replace_labels(self):
        for cmd in self._cmds:
            for arg in cmd['ARGS']:
                if arg['TYPE'] == 'LABEL':
                    constant = self._labels[arg['LABEL']]
                    arg['TYPE'] = 'CONSTANT'
                    arg['STR'] = str(constant)
                    arg['CONSTANT'] = constant

    def generate_code(self):
        self.replace_labels()
        return '\n'.join([self.command_str(cmd) for cmd in self._cmds])

    @classmethod
    def command_str(cls, cmd):
        args = [arg['STR'] for arg in cmd['ARGS']]
        return '%s %s' % (cmd['COMMAND'], ','.join(args))

    def program(self):
        self.replace_labels()
        return self._cmds
    
if __name__ == '__main__':
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as f:
            parser = Parser()
            parser.parse_file(f)
            print parser.generate_code()
    else:
        print 'usage: %s input_file' % os.path.basename(sys.argv[0])
