#!/usr/bin/env python

import sys
import os
import os.path

import ghost

REGISTERS = 'abcdefgh'
IRQ_NBR = 9

class ExecutionError(Exception):
    pass

class Simulator(object):
    def __init__(self):
        self.reset()
        self._cmd_handler = {
            'MOV': self._ch_mov,
            'INC': self._ch_inc,
            'DEC': self._ch_dec,
            'ADD': self._ch_add,
            'SUB': self._ch_sub,
            'MUL': self._ch_mul,
            'DIV': self._ch_div,
            'AND': self._ch_and,
            'OR' : self._ch_or,
            'XOR': self._ch_xor,
            'JLT': self._ch_jlt,
            'JEQ': self._ch_jeq,
            'JGT': self._ch_jgt,
            'INT': self._ch_int,
            'HLT': self._ch_hlt}
        self._irq_handler = dict([(irq, self._irqh_nop) for irq in range(IRQ_NBR)])

    def reset(self):
        self._halt = False
        self._memory = 256 * [0]
        self._reg = dict([(c, 0) for c in REGISTERS])
        self._pc = 0
        self._next_cmd = None
        self._instruction_count = 0
        self._program = []

    def load(self, program):
        self.reset()
        self._program = program
        self._next_cmd = self._program[0]

    def load_file(self, f):
        parser = ghost.Parser()
        parser.parse_file(f)
        self.load(parser.program())

    def state_str(self):
        s = []
        s.append('Size:  %4d' % len(self._program))
        s.append('Count: %4d' % self._instruction_count)
        s.append(' ')
        for registers in (REGISTERS[:4], REGISTERS[4:]):
            s.append('   '.join(['%s[%3d]' % (reg, self._reg[reg]) for reg in registers]))
        s.append(' ')
        for i in range(0, 256, 16):
            s.append(('[%3d]  ' % i) + '  '.join(['%3d' % self._memory[i + j] for j in range(16)]))
        s.append(' ')
        s.append('pc[%4d]: %s' % (self._pc, ghost.Parser.command_str(self._next_cmd)))
        return '\n'.join(s)

    def install_interactive_irq_handlers(self):
        for irq in range(IRQ_NBR):
            self._irq_handler[irq] = getattr(self, '_irqh_interactive_%d' % irq)

    def _irqh_nop(self, reg):
        pass

    def _irqh_interactive_0(self, reg):
        print 'IRQ0'
        print 'reg a (new direction): %d' % reg['a']
        print
        print '0: up'
        print '1: right'
        print '2: down'
        print '3: left'
        print
        raw_input('> ')
    
    def _irqh_interactive_1(self, reg):
        print 'IRQ1'
        print
        reg['a'] = self._get_int_input('reg a (lambda 1 x)> ')
        reg['b'] = self._get_int_input('reg b (lambda 1 y)> ')
    
    def _irqh_interactive_2(self, reg):
        print 'IRQ2'
        print
        reg['a'] = self._get_int_input('reg a (lambda 2 x)> ')
        reg['b'] = self._get_int_input('reg b (lambda 2 y)> ')
    
    def _irqh_interactive_3(self, reg):
        print 'IRQ3'
        print
        reg['a'] = self._get_int_input('reg a (ghost index)> ')
    
    def _irqh_interactive_4(self, reg):
        print 'IRQ4'
        print 'reg a (ghost index): %d' % reg['a']
        print
        reg['a'] = self._get_int_input('reg a (ghost start x)> ')
        reg['b'] = self._get_int_input('reg b (ghost start y)> ')
    
    def _irqh_interactive_5(self, reg):
        print 'IRQ5'
        print 'reg a (ghost index): %d' % reg['a']
        print
        reg['a'] = self._get_int_input('reg a (ghost current x)> ')
        reg['b'] = self._get_int_input('reg b (ghost current y)> ')
    
    def _irqh_interactive_6(self, reg):
        print 'IRQ6'
        print 'reg a (ghost index): %d' % reg['a']
        print
        print '0: standard'
        print '1: fright mode'
        print '2: invisible'
        print
        reg['a'] = self._get_int_input('reg a (ghost vitality)> ')
        print
        print '0: up'
        print '1: right'
        print '2: down'
        print '3: left'
        print
        reg['b'] = self._get_int_input('reg b (ghost direction)> ')
    
    def _irqh_interactive_7(self, reg):
        print 'IRQ7'
        print 'reg a (map x): %d' % reg['a']
        print 'reg b (map y): %d' % reg['b']
        print
        print '0: wall'
        print '1: empty'
        print '2: pill'
        print '3: power pill'
        print '4: fruit'
        print '5: lambda start'
        print '6: ghost start'
        print
        reg['a'] = self._get_int_input('reg a (map contents)> ')
    
    def _irqh_interactive_8(self, reg):
        print 'IRQ8'
        for r in REGISTERS:
            print 'reg %s: %d' % (r, reg[r])
        raw_input('> ')

    def _get_int_input(self, prompt):
        value = None
        while value is None:
            try:
                value = int(raw_input(prompt))
            except ValueError:
                pass
        return value

    def _fetch(self, src):
        src_type = src['TYPE']
        if src_type == 'REGISTER':
            register = src['REGISTER']
            if register == 'pc':
                return self._pc
            else:
                return self._reg[register]
        elif src_type == 'INDIRECT':
            register = src['REGISTER']
            address = self._reg[register]
            return self._memory[address]
        elif src_type == 'MEMORY':
            address = src['ADDRESS']
            return self._memory[address]
        elif src_type == 'CONSTANT':
            return src['CONSTANT']
        raise ExecutionError('Invalid source argument type: %s' % src_type)

    def _store(self, dest, value):
        value = (value + 256) % 256
        dest_type = dest['TYPE']
        if dest_type == 'REGISTER':
            register = dest['REGISTER']
            self._reg[register] = value
        elif dest_type == 'INDIRECT':
            register = dest['REGISTER']
            address = self._reg[register]
            self._memory[address] = value
        elif dest_type == 'MEMORY':
            address = dest['ADDRESS']
            self._memory[address] = value
        else:
            raise ExecutionError('Invalid destination argument type: %s' % dest_type)

    def _ch_mov(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(src))
        self._inc_pc()

    def _ch_inc(self, args):
        assert len(args) == 1
        dest = args[0]
        self._store(dest, self._fetch(dest) + 1)
        self._inc_pc()

    def _ch_dec(self, args):
        assert len(args) == 1
        dest = args[0]
        self._store(dest, self._fetch(dest) - 1)
        self._inc_pc()

    def _ch_add(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(dest) + self._fetch(src))
        self._inc_pc()

    def _ch_sub(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(dest) - self._fetch(src))
        self._inc_pc()

    def _ch_mul(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(dest) * self._fetch(src))
        self._inc_pc()

    def _ch_div(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(dest) / self._fetch(src))
        self._inc_pc()

    def _ch_and(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(dest) & self._fetch(src))
        self._inc_pc()

    def _ch_or(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(dest) | self._fetch(src))
        self._inc_pc()

    def _ch_xor(self, args):
        assert len(args) == 2
        dest = args[0]
        src = args[1]
        self._store(dest, self._fetch(dest) ^ self._fetch(src))
        self._inc_pc()

    def _ch_jlt(self, args):
        assert len(args) == 3
        targ = args[0]
        assert targ['TYPE'] == 'CONSTANT'
        x = args[1]
        y = args[2]
        if self._fetch(x) < self._fetch(y):
            self._set_pc(self._fetch(targ))
        else:
            self._inc_pc()

    def _ch_jeq(self, args):
        assert len(args) == 3
        targ = args[0]
        assert targ['TYPE'] == 'CONSTANT'
        x = args[1]
        y = args[2]
        if self._fetch(x) == self._fetch(y):
            self._set_pc(self._fetch(targ))
        else:
            self._inc_pc()

    def _ch_jgt(self, args):
        assert len(args) == 3
        targ = args[0]
        assert targ['TYPE'] == 'CONSTANT'
        x = args[1]
        y = args[2]
        if self._fetch(x) > self._fetch(y):
            self._set_pc(self._fetch(targ))
        else:
            self._inc_pc()

    def _ch_int(self, args):
        assert len(args) == 1
        irq = args[0]
        irq_handler = self._irq_handler[self._fetch(irq)]
        irq_handler(self._reg)
        self._inc_pc()

    def _ch_hlt(self, args):
        assert len(args) == 0
        self._halt = True

    def _inc_pc(self):
        self._set_pc(self._pc + 1)

    def _set_pc(self, new_pc):
        self._pc = new_pc
        self._next_cmd = self._program[new_pc]

    def step(self, n=1):
        for i in range(n):
            if not self._halt:
                cmd = self._next_cmd['COMMAND']
                args = self._next_cmd['ARGS']
                cmd_handler = self._cmd_handler[cmd]
                cmd_handler(args)
                self._instruction_count += 1

    def run_to_line(self, nbr):
        while not self._halt and nbr != self._next_cmd['NBR']:
            self.step()

    def run_to_pc(self, pc):
        while not self._halt and pc != self._pc:
            self.step()

    def run_interactive(self):
        self.install_interactive_irq_handlers()
        cmd = None
        while cmd != 'q':
            os.system('cls' if os.name == 'nt' else 'clear')
            print self.state_str()
            print
            if cmd == 'h':
                print 'enter     step'
                print 'b <pc>    run and break at pc'
                print 'g <line>  run to line (source)'
                print 's <n>     run n steps'
                print
                print 'h         show help'
                print 'q         quit'
                print
            cmd = raw_input('> ')
            if cmd == '':
                self.step()
            elif cmd.startswith('b'):
                try:
                    pc = int(cmd[1:])
                except ValueError:
                    pass
                else:
                    self.run_to_pc(pc)
            elif cmd.startswith('g'):
                try:
                    line = int(cmd[1:])
                except ValueError:
                    pass
                else:
                    self.run_to_line(line)
            elif cmd.startswith('s'):
                try:
                    n = int(cmd[1:])
                except ValueError:
                    pass
                else:
                    self.step(n)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as f:
            simulator = Simulator()
            simulator.load_file(f)
            simulator.run_interactive()
    else:
        print 'usage: %s program_file' % os.path.basename(sys.argv[0])
