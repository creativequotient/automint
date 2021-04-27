import unittest

from automint.account import Account


class AccountTests(unittest.TestCase):
    def test_lovelace_addition(self):
        """
        Test that it can sum a list of integers
        """
        account = Account().add_lovelace(1000)
        self.assertEqual(account.get_lovelace(), 1000)
        self.assertEqual(account.get_ada(), 0.001)

if __name__ == '__main__':
    unittest.main()
