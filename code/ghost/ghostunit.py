import unittest

import ghostsim

VITALITY_STANDARD = 0
VITALITY_FRIGHT = 1
VITALITY_INVISIBLE = 2

MV_UP = 0
MV_RIGHT = 1
MV_DOWN = 2
MV_LEFT = 3

MAP_WALL = 0
MAP_EMPTY = 1
MAP_PILL = 2
MAP_POWER_PILL = 3
MAP_FRUIT = 4
MAP_LAMBDA_MAN_START = 5
MAP_GHOST_START = 6

class GhostUnit(unittest.TestCase):
    def irq_handler_0(self, reg):
        self.move = reg['a']

    def irq_handler_1(self, reg):
        reg['a'] = self.lambda_1_x
        reg['b'] = self.lambda_1_y

    def irq_handler_2(self, reg):
        reg['a'] = self.lambda_2_x
        reg['b'] = self.lambda_2_y

    def irq_handler_3(self, reg):
        reg['a'] = self.ghost_index

    def irq_handler_4(self, reg):
        self.assertEqual(self.ghost_index, reg['a'])
        reg['a'] = self.ghost_start_x
        reg['b'] = self.ghost_start_y

    def irq_handler_5(self, reg):
        self.assertEqual(self.ghost_index, reg['a'])
        reg['a'] = self.ghost_x
        reg['b'] = self.ghost_y

    def irq_handler_6(self, reg):
        self.assertEqual(self.ghost_index, reg['a'])
        reg['a'] = self.ghost_vitality
        reg['b'] = self.ghost_direction

    def irq_handler_7(self, reg):
        x = reg['a']
        y = reg['b']
        reg['a'] = self.map(x, y)

    def irq_handler_8(self, reg):
        pass

    def map(self, x, y):
        return MAP_WALL

    def init(self):
        self.sim = ghostsim.Simulator()
        for irq in range(ghostsim.IRQ_NBR):
            self.sim.set_irq_handler(irq, getattr(self, 'irq_handler_%d' % irq))
        self.move = None
        self.ghost_index = 0
        self.ghost_start_x = 0
        self.ghost_start_y = 0
        self.ghost_x = 0
        self.ghost_y = 0
        self.ghost_vitality = VITALITY_STANDARD
        self.ghost_direction = MV_UP
        self.lambda_1_x = 0
        self.lambda_1_y = 0
        self.lambda_2_x = 0
        self.lambda_2_y = 0

    def load_file(self, filename):
        with open(filename, 'r') as f:
            self.sim.load_file(f)
