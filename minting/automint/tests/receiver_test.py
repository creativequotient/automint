from automint.Account import Account
from automint.UTXO import UTXO
from automint.Receiver import Receiver

if __name__ == '__main__':

    receiver_a = Receiver('abc123efg578')
    receiver_a.add_ada(5)
    receiver_a.add_native_token('123456.sampleToken01', 2)
    print(receiver_a)

    receiver_b = receiver_a.get_blank_receiver()
    print(receiver_b)
