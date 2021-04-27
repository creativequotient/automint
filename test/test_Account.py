import unittest

from automint.account import Account


class AccountTests(unittest.TestCase):
    def test_lovelace_addition(self):
        account = Account().add_lovelace(1000)
        self.assertEqual(account.get_lovelace(), 1000)
        self.assertEqual(account.get_ada(), 0.001)

    def test_account_addition(self):
        account_a = Account().add_lovelace(1500000)
        account_b = Account().add_lovelace(1500000)
        account_c = account_a + account_b
        self.assertEqual(account_c.get_lovelace(), 3000000)
        self.assertEqual(account_c.get_ada(), 3)

    def test_account_str(self):
        account = Account().add_lovelace(1500000)
        self.assertEqual(str(account), '1500000')

        account = Account().add_lovelace(1500000).add_native_token('12345.tokenA', 2)
        self.assertEqual(str(account), '1500000+"2 12345.tokenA"')


if __name__ == '__main__':
    unittest.main()
