import unittest

from pokemon.demo.demo_class import DemoClass

class TestDemoClass(unittest.TestCase):

    def test_add(self):
        for a in range(-10, 10):
            for b in range(-10, 10):
                self.assertEqual(a + b, DemoClass.add(a, b))


                