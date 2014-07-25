#!/usr/bin/env python

import unittest

import ghost

class TestGhost(unittest.TestCase):
    def test_parse_comment(self):
        result = ghost.parse_line(' ; Comment')
        self.assertEqual(result[0], 'EMPTY')
        
    def test_parse_label(self):
        result = ghost.parse_line('label: ; Label')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'LABEL')
        self.assertEqual(result[1], 'label')
        
    def test_parse_invalid_label(self):
        with self.assertRaises(ghost.ParseError) as error:
            result = ghost.parse_line('2label: ; Invalid label')
            
    def test_parse_cmd_no_args(self):
        result = ghost.parse_line('HLT ; No arguments')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'COMMAND')
        self.assertEqual(result[1], 'HLT')
        args = result[2]
        self.assertEqual(len(args), 0)
        
    def test_parse_cmd_single_arg(self):
        result = ghost.parse_line('INC a; Single argument')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'COMMAND')
        self.assertEqual(result[1], 'INC')
        args = result[2]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0][0], 'ARG')
        self.assertEqual(args[0][1], 'a')
        
    def test_parse_cmd_multiple_args(self):
        result = ghost.parse_line('JEQ 0,1,2; Multiple arguments')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'COMMAND')
        self.assertEqual(result[1], 'JEQ')
        args = result[2]
        self.assertEqual(len(args), 3)
        for i in range(3):
            self.assertEqual(args[i][0], 'ARG')
            self.assertEqual(args[i][1], str(i))
            
    def test_parse_too_many_args(self):
        with self.assertRaises(ghost.ParseError) as error:
            result = ghost.parse_line('JEQ 0,1,2,3; Too many arguments')
            
    def test_parse_label_arg(self):
        result = ghost.parse_line('JEQ #label,1,2; Label argument')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'COMMAND')
        self.assertEqual(result[1], 'JEQ')
        args = result[2]
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0][0], 'LABEL')
        self.assertEqual(args[0][1], 'label')
        for i in range(1, 3):
            self.assertEqual(args[i][0], 'ARG')
            self.assertEqual(args[i][1], str(i))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGhost)
    unittest.TextTestRunner(verbosity=2).run(suite)
