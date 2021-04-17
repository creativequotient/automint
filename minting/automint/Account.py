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

        # Check if token exists within Account
        if token_id not in self.native_tokens:
            return self

        new_account = copy.deepcopy(self)
        new_account.native_tokens[token_id]['quantity'] -= quantity

        if new_account.native_tokens[token_id]['quantity'] == 0:
            new_account.native_tokens.pop(token_id)

        return new_account

    def set_native_token(self, token_id, quantity):
        assert quantity > 0

        new_account = copy.deepcopy(self)
        policy_id, token = token_id.split('.')
        new_account.native_tokens[toke_id] = {
            'name': token,
            'policy_id': policy_id,
            'quantity': quantity
        }

        return new_account

    def add_lovelace(self, quantity):
        assert quantity > 0

        new_account = copy.deepcopy(self)
        new_account.lovelace += quantity

        return new_account

    def remove_lovelace(self, quantity):
        assert quantity > 0

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
        return self.add_lovelace(quantity * 1000000)

    def remove_ada(self, quantity):
        return self.remove_lovelace(quantity * 1000000)

    def set_ada(self, quantity):
        return self.set_lovelace(quantity * 1000000)

    def __str__(self):
        assets = []
        for token_id in sorted(self.native_tokens.keys()):
            assets.append(f'{self.native_tokens[token_id]["quantity"]} {token_id}')

        output = f'{self.lovelace}'
        if len(assets) != 0:
            output += f'+"{" + ".join(assets)}"'

        return output
