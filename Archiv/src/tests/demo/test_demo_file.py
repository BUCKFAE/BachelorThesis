import unittest

from pokemon.demo import demo_file

class TestDemoFile(unittest.TestCase):

    def test_divide(self):
        for a in range(-10, 10):
            for b in range(-10, 10):
                if b == 0: continue
                self.assertEqual(a / b, demo_file.divide(a, b))