#!/usr/bin/env python

import unittest

import ghostunit as gu

class TestGhost(gu.GhostUnit):
    def setUp(self):
        self.init()
        self.load_file('ai_2.ghc')
        self.map_sq = gu.MAP_EMPTY

    def map(self, x, y):
        return self.map_sq

    def test_invisible_mode(self):
        self.ghost_vitality = gu.VITALITY_INVISIBLE
        self.sim.run()
        self.assertIsNone(self.move)

    def test_random_move(self):
        self.ghost_vitality = gu.VITALITY_STANDARD
        self.ghost_direction = gu.MV_UP
        self.ghost_index = 0
        self.ghost_x = 5
        self.ghost_y = 5
        self.lambda_1_x = 20
        self.lambda_1_y = 20
        self.sim.run()
        self.assertEqual(self.move, gu.MV_LEFT)
        self.sim.reset(keep_program=True)
        self.ghost_direction = gu.MV_LEFT
        self.ghost_index = 1
        self.sim.run()
        self.assertEqual(self.move, gu.MV_DOWN)
        self.sim.reset(keep_program=True)
        self.ghost_direction = gu.MV_DOWN
        self.ghost_index = 2
        self.sim.run()
        self.assertEqual(self.move, gu.MV_RIGHT)
        self.sim.reset(keep_program=True)
        self.ghost_direction = gu.MV_RIGHT
        self.ghost_index = 3
        self.sim.run()
        self.assertEqual(self.move, gu.MV_UP)

    def test_normal_mode_valid_move(self):
        self.ghost_vitality = gu.VITALITY_STANDARD
        self.ghost_direction = gu.MV_RIGHT
        self.ghost_x = 5
        self.ghost_y = 5
        self.lambda_1_x = 8
        self.lambda_1_y = 10
        self.sim.run()
        self.assertEqual(self.move, gu.MV_DOWN)
        self.sim.reset(keep_program=True)
        self.ghost_direction = gu.MV_UP
        self.lambda_1_x = 10
        self.lambda_1_y = 8
        self.sim.run()
        self.assertEqual(self.move, gu.MV_RIGHT)

    def test_normal_mode_invalid_turn(self):
        self.ghost_vitality = gu.VITALITY_STANDARD
        self.ghost_direction = gu.MV_UP
        self.ghost_x = 5
        self.ghost_y = 5
        self.lambda_1_x = 8
        self.lambda_1_y = 10
        self.sim.run()
        self.assertEqual(self.move, gu.MV_RIGHT)

    def test_normal_mode_invalid_move_wall(self):
        self.ghost_vitality = gu.VITALITY_STANDARD
        self.ghost_direction = gu.MV_RIGHT
        self.ghost_x = 5
        self.ghost_y = 5
        self.lambda_1_x = 8
        self.lambda_1_y = 10
        self.map_sq = gu.MAP_WALL
        self.sim.run()
        self.assertEqual(self.move, gu.MV_RIGHT)
        
    def test_fright_mode_valid_move(self):
        self.ghost_vitality = gu.VITALITY_FRIGHT
        self.ghost_direction = gu.MV_LEFT
        self.ghost_index = 1
        self.ghost_x = 5
        self.ghost_y = 5
        self.lambda_1_x = 10
        self.lambda_1_y = 20
        self.sim.run()
        self.assertEqual(self.move, gu.MV_UP)
        self.sim.reset(keep_program=True)
        self.ghost_direction = gu.MV_UP
        self.lambda_1_x = 20
        self.lambda_1_y = 10
        self.sim.run()
        self.assertEqual(self.move, gu.MV_LEFT)

    def test_fright_mode_invalid_turn(self):
        self.ghost_vitality = gu.VITALITY_FRIGHT
        self.ghost_direction = gu.MV_DOWN
        self.ghost_index = 1
        self.ghost_x = 5
        self.ghost_y = 5
        self.lambda_1_x = 10
        self.lambda_1_y = 20
        self.sim.run()
        self.assertEqual(self.move, gu.MV_LEFT)

    def test_fright_mode_invalid_move_wall(self):
        self.ghost_vitality = gu.VITALITY_FRIGHT
        self.ghost_direction = gu.MV_LEFT
        self.ghost_index = 1
        self.ghost_x = 5
        self.ghost_y = 5
        self.lambda_1_x = 10
        self.lambda_1_y = 20
        self.map_sq = gu.MAP_WALL
        self.sim.run()
        self.assertEqual(self.move, gu.MV_LEFT)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGhost)
    unittest.TextTestRunner(verbosity=2).run(suite)
