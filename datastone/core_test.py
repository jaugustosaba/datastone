import unittest
import random
import math
from .core import Conversor

__doc__ = '''
core test cases
'''

class ConversorTest(unittest.TestCase):
    "conversor test case"

    def setUp(self):
        self.conversor = Conversor(
            reference='BRL',
            currencies={
                'BRL': 1.0,
                'USD': 10.0,
                'GBP': 15.0,
            },
        )
    
    def assertFloatEqual(self, n: float, m: float):
        "float equality test"
        self.assertTrue(math.fabs(n - m) < 1E-6)

    def test_reflexive(self):
        "A currency value converted to itself must return the same value"
        self.assertEqual(31415, self.conversor.convert('BRL', 'BRL', 31415))

    def test_reference_conversion(self):
        "Tests conversion from and to reference currency"
        self.assertEqual(10.0, self.conversor.convert('USD', 'BRL', 1.0))
        self.assertEqual(15.0, self.conversor.convert('GBP', 'BRL', 1.0))
        self.assertEqual(1.0, self.conversor.convert('BRL', 'USD', 10.0))
        self.assertEqual(1.0, self.conversor.convert('BRL', 'GBP', 15.0))

    def test_linearity(self):
        "The conversion must be linear"
        n = random.randint(2, 20)
        amount = random.randint(100, 200)
        from_currency = 'BRL'
        to_currency = 'USD'
        value = self.conversor.convert(from_currency, to_currency, amount)
        self.assertEqual(value * n, self.conversor.convert(from_currency, to_currency, n * amount))

    def test_transitive_conversion(self):
        "Tests convertion from currencies without using explicitly the reference"
        self.assertEqual(10, self.conversor.convert('USD', 'GBP', 15))

    def test_unknown_currency(self):
        "Unknown currencies must raise exceptions"
        with self.assertRaises(Exception):
            self.conversor.convert('CAD', 'GBP', 100)


if __name__ == '__main__':
    unittest.main()