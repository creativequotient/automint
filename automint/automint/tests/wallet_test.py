from automint.Account import Account
from automint.UTXO import UTXO

if __name__ == '__main__':

    # UTXO A
    utxo_a = UTXO('abcdefg67880 0 5000 lovelace + 1 12345.sampleToken01 + 1 12345.sampleToken02')
    print(utxo_a)
    print(utxo_a.get_account())
