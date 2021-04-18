from automint.account import Account
from automint.receivers import BasicReceiver


# The TxReceiver class is used to generate the string formated output
# for the `--tx-out` field. It should be used to keep track of the
# tokens during transactions, all assets consumed by the input UTXOs
# must match all assets output by all the TxReceivers in a transation.
class TxReceiver(BasicReceiver):
    def __init__(self, addr):
        super().__init__()
        self.addr = addr

    def get_blank_receiver(self):
        new_receiver = self.duplicate()
        new_receiver.set_ada(0)
        return new_receiver

    def set_address(self, addr):
        new_recevier = self.duplicate()
        new_recevier.addr = addr
        return new_recevier

    def __str__(self):
        return f'{self.addr}+{self.account}'
