import copy
from automint.account import Account


# The BasicReceiver class contains the minimal functionality for
# artithmetic on token quantities
class BasicReceiver(object):
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

    def transfer_to(self, other_receiver):
        '''Transfer the convents of this receiver to another receiver,
        emptying this one'''
        other_receiver.account = self.account + other_receiver.account
        self.account = Account()

    def get_lovelace(self):
        return self.account.get_lovelace()

    def get_native_token(self, token_id):
        return self.account.get_native_token(token_id)
