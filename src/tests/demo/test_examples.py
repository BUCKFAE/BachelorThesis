import unittest

class TestExamples(unittest.TestCase):
    """Demo Tests for simple validation"""
    
    def test_assert_equal(self):
        self.assertEqual(1, 1)

    def test_assert_true(self):
        self.assertTrue(True)

    def test_assert_false(self):
        self.assertFalse(False)

if __name__ == "__main__":
    unittest.main()