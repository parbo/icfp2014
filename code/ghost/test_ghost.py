#!/usr/bin/env python

import unittest

import ghost

class TestGhost(unittest.TestCase):
    def setUp(self):
        self.p = ghost.Parser()

    def test_parse_comment(self):
        result = self.p.parse_line(' ; Comment')
        self.assertEqual(result['TYPE'], 'EMPTY')
        
    def test_parse_label(self):
        result = self.p.parse_line('label: ; Label')
        self.assertEqual(len(result), 2)
        self.assertEqual(result['TYPE'], 'LABEL')
        self.assertEqual(result['LABEL'], 'label')
        
    def test_parse_invalid_label(self):
        with self.assertRaises(ghost.ParseError) as error:
            result = self.p.parse_line('2label: ; Invalid label')
            
    def test_parse_cmd_no_args(self):
        result = self.p.parse_line('HLT ; No arguments')
        self.assertEqual(len(result), 3)
        self.assertEqual(result['TYPE'], 'COMMAND')
        self.assertEqual(result['COMMAND'], 'HLT')
        args = result['ARGS']
        self.assertEqual(len(args), 0)
        
    def test_parse_cmd_single_arg(self):
        result = self.p.parse_line('INC a; Single argument')
        self.assertEqual(len(result), 3)
        self.assertEqual(result['TYPE'], 'COMMAND')
        self.assertEqual(result['COMMAND'], 'INC')
        args = result['ARGS']
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0]['TYPE'], 'REGISTER')
        self.assertEqual(args[0]['REGISTER'], 'a')
        
    def test_parse_cmd_multiple_args(self):
        result = self.p.parse_line('JEQ 0,1,2; Multiple arguments')
        self.assertEqual(len(result), 3)
        self.assertEqual(result['TYPE'], 'COMMAND')
        self.assertEqual(result['COMMAND'], 'JEQ')
        args = result['ARGS']
        self.assertEqual(len(args), 3)
        for i in range(3):
            self.assertEqual(args[i]['TYPE'], 'CONSTANT')
            self.assertEqual(args[i]['CONSTANT'], i)
            
    def test_parse_too_many_args(self):
        with self.assertRaises(ghost.ParseError) as error:
            result = self.p.parse_line('JEQ 0,1,2,3; Too many arguments')
            
    def test_parse_label_arg(self):
        result = self.p.parse_line('JEQ #label,1,2; Label argument')
        self.assertEqual(len(result), 3)
        self.assertEqual(result['TYPE'], 'COMMAND')
        self.assertEqual(result['COMMAND'], 'JEQ')
        args = result['ARGS']
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0]['TYPE'], 'LABEL')
        self.assertEqual(args[0]['LABEL'], 'label')
        for i in range(1, 3):
            self.assertEqual(args[i]['TYPE'], 'CONSTANT')
            self.assertEqual(args[i]['CONSTANT'], i)

    def test_invalid_arg(self):
        with self.assertRaises(ghost.ParseError) as error:
            result = self.p.parse_line('INC [ab]; Invalid arguments')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGhost)
    unittest.TextTestRunner(verbosity=2).run(suite)
