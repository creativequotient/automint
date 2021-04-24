import copy


class Account(object):
    '''The Account class is used to keep track of a set of tokens and
    supports arithmetic on the tokens.

    '''
    def __init__(self):
        self.lovelace = 0
        self.native_tokens = {}

    def add_native_token(self, token_id, quantity):
        assert quantity > 0

        new_account = copy.deepcopy(self)

        if token_id not in new_account.native_tokens:
            policy_id, token = token_id.split('.')
            new_account.native_tokens[token_id] = {
                'name': token,
                'policy_id': policy_id,
                'quantity': 0
            }

        new_account.native_tokens[token_id]['quantity'] += quantity

        return new_account

    def remove_native_token(self, token_id, quantity):
        assert quantity > 0

        new_account = copy.deepcopy(self)

        if token_id not in new_account.native_tokens:
            policy_id, token = token_id.split('.')
            new_account.native_tokens[token_id] = {
                'name': token,
                'policy_id': policy_id,
                'quantity': 0
            }

        new_account.native_tokens[token_id]['quantity'] -= quantity

        if new_account.native_tokens[token_id]['quantity'] == 0:
            new_account.native_tokens.pop(token_id)

        return new_account

    def set_native_token(self, token_id, quantity):
        assert quantity > 0

        new_account = copy.deepcopy(self)
        policy_id, token = token_id.split('.')
        new_account.native_tokens[token_id] = {
            'name': token,
            'policy_id': policy_id,
            'quantity': quantity
        }

        if new_account.native_tokens[token_id]['quantity'] == 0:
            new_account.native_tokens.pop(token_id)

        return new_account

    def add_lovelace(self, quantity):
        assert quantity >= 0

        new_account = copy.deepcopy(self)
        new_account.lovelace += quantity

        return new_account

    def remove_lovelace(self, quantity):
        assert quantity >= 0

        new_account = copy.deepcopy(self)
        new_account.lovelace -= quantity

        return new_account

    def set_lovelace(self, quantity):
        assert quantity >= 0

        new_account = copy.deepcopy(self)
        new_account.lovelace = quantity

        return new_account


    def set_ada(self, quantity):
        assert quantity >= 0

        new_account = copy.deepcopy(self)
        new_account.lovelace = quantity

        return new_account

    def add_ada(self, quantity):
        return self.add_lovelace(int(quantity * 1000000))

    def remove_ada(self, quantity):
        return self.remove_lovelace(int(quantity * 1000000))

    def set_ada(self, quantity):
        return self.set_lovelace(int(quantity * 1000000))

    def __str__(self):
        assets = []
        for token_id in sorted(self.native_tokens.keys()):
            assets.append(f'{self.native_tokens[token_id]["quantity"]} {token_id}')

        output = f'{self.lovelace}'
        if len(assets) != 0:
            output += f'+"{" + ".join(assets)}"'

        return output

    def size(self):
        return 1 + len(self.native_tokens)

    def get_lovelace(self):
        return self.lovelace

    def get_ada(self):
        return self.lovelace / 1000000

    def get_native_token(self, token_id):
        return self.native_tokens.get(token_id, 0)

    def duplicate(self):
        new_account = copy.deepcopy(self)
        return new_account

    def __add__(self, other_account):
        new_account = Account()
        new_account = new_account.add_lovelace(self.get_lovelace())
        new_account = new_account.add_lovelace(other_account.get_lovelace())
        for token_id in self.native_tokens.keys():
            new_account = new_account.add_native_token(token_id, self.get_native_token(token_id)['quantity'])
        for token_id in other_account.native_tokens.keys():
            new_account = new_account.add_native_token(token_id, other_account.get_native_token(token_id)['quantity'])
        return new_account