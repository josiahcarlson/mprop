
import unittest

import example
import example2

class TestMprop(unittest.TestCase):
    def test_property_init(self):
        self.assertEqual(example.test_read, "got read")
        example.test_read = 'world'
        self.assertEqual(example.value, "world")

    def test_mproperty(self):
        self.assertEqual(example2.test_read, "got read")
        example2.test_read = 'world'
        self.assertEqual(example2.value, "world")

if __name__ == '__main__':
    unittest.main()
