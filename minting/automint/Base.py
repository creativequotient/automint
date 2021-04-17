import copy
from automint.Account import Account


class Base(object):
    def __init__(self):
        self.account = Account()

    def get_account(self):
        return self.account

    def add_ada(self, quantity):
        self.account = self.account.add_ada(quantity)

    def remove_ada(self, quantity):
        self.account = self.account.remove_ada(quantity)

    def add_lovelace(self, quantity):
        self.account = self.account.add_lovelace(quantity)

    def remove_lovelace(self, quantity):
        self.account = self.account.remove_lovelace(quantity)

    def add_native_token(self, token_id, quantity):
        self.account = self.account.add_native_token(token_id, quantity)

    def remove_native_token(self, token_id, quantity):
        self.account = self.account.remove_native_token(token_id, quantity)

    def set_ada(self, quantity):
        self.account = self.account.set_ada(quantity)

    def set_native_token(self, token_id, quantity):
        self.account = self.account.set_native_token(token_id, quantity)

    def duplicate(self):
        return copy.deepcopy(self)
