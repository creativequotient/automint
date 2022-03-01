from automint.account import Account
from automint.receivers import BasicReceiver

from automint.utils import convert_to_hex


# The MintingReceiver class is used to generate the string formatted
# output for the `--mint` field. It should be used to keep track of
# tokens for minting and burning.
class MintingReceiver(BasicReceiver):
    def __init__(self):
        super().__init__()

    def add_ada(self, quantity):
        raise Exception('This method should not be called.')

    def add_lovelace(self, quantity):
        raise Exception('This method should not be called.')

    def remove_ada(self, quantity):
        raise Exception('This method should not be called.')

    def remove_lovelace(self, quantity):
        raise Exception('This method should not be called.')

    def __str__(self):
        assets = []
        account = self.get_account()
        for token_id in sorted(account.native_tokens.keys()):
            policy_id, ticker = token_id.split('.')
            ticker_hex = convert_to_hex(ticker)

            token_hex = f'{policy_id}.{ticker_hex}'
            assets.append(f'{account.native_tokens[token_id]["quantity"]} {token_hex}')
        return f'"{" + ".join(assets)}"'
