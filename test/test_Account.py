import unittest

from automint.account import Account


class AccountTests(unittest.TestCase):
    def test_lovelace_addition(self):
        account = Account().add_lovelace(1000)
        self.assertEqual(account.get_lovelace(), 1000)
        self.assertEqual(account.get_ada(), 0.001)

    def test_account_addition(self):
        '''This test checks for the addition of lovelace'''
        account_a = Account().add_lovelace(1500000)
        account_b = Account().add_lovelace(1500000)
        account_c = Account().add_lovelace(3000000)
        self.assertEqual(account_a + account_b, account_c)

    def test_account_str(self):
        '''This test checks for proper conversion of Account objects to string representation'''

        # Only contains lovelace
        account = Account().add_lovelace(1500000)
        self.assertEqual(str(account), '1500000')

        # Contains lovelace and a native token
        account = Account().add_lovelace(1500000)
        account = account.add_native_token('12345.tokenA', 2)
        self.assertEqual(str(account), '1500000+"2 12345.tokenA"')

        # Contains lovelace and a native token (added separately)
        account = Account().add_lovelace(1500000)
        account = account.add_native_token('12345.tokenA', 2)
        account = account.add_native_token('12345.tokenA', 2)
        self.assertEqual(str(account), '1500000+"4 12345.tokenA"')

        # Contains lovelace and different native tokens
        account = Account().add_lovelace(1500000)
        account = account.add_native_token('12345.tokenA', 2)
        account = account.add_native_token('56789.tokenA', 2)
        self.assertEqual(str(account), '1500000+"2 12345.tokenA + 2 56789.tokenA"')

        # Negative quantities for burning
        account = Account().add_lovelace(1500000)
        account = account.add_native_token('12345.tokenA', 2)
        account = account.remove_native_token('56789.tokenA', 2)
        self.assertEqual(str(account), '1500000+"2 12345.tokenA + -2 56789.tokenA"')
