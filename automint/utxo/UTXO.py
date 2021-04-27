import copy
from automint.account import Account
from automint.receivers import TxReceiver


class UTXO(object):
    def __init__(self, utxo_str):
        self.txHash = None
        self.index = None
        self.account = None
        self.parse_utxo_str(utxo_str)

        assert self.txHash != None
        assert self.index != None
        assert self.account != None

    def parse_utxo_str(self, utxo_str):
        # Split raw utxo string
        utxo_str = utxo_str.split(maxsplit=2)

        # Get txHash and index
        self.txHash = utxo_str[0]
        self.index = int(utxo_str[1])

        # Create account
        self.account = Account()

        # Parse tokens component
        tokens_str = utxo_str[2].split('+')

        # Extract lovelace
        lovelace = int(tokens_str[0].replace('lovelace', '').strip())
        self.account = self.account.add_lovelace(lovelace)

        # Extract native_tokens
        if len(tokens_str) >= 2:
            native_assets_str = tokens_str[1:]
            for native_asset_str in native_assets_str:
                qty, asset = native_asset_str.strip().split()
                qty = int(qty)
                self.account = self.account.add_native_token(asset, qty)

    def get_utxo_identifier(self):
        return f'{self.txHash}#{self.index}'

    def get_account(self):
        return self.account

    def __str__(self):
        return f'{self.get_utxo_identifier()}'

    def convert_to_receiver(self, addr):
        '''Converts UTXO to TxReceiver object, copying all contents over'''
        new_receiver = TxReceiver(addr)
        new_receiver.account = self.account.duplicate()
        return new_receiver

    def size(self):
        return self.account.size()
