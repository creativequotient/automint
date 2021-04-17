from automint.Account import Account
from automint.Base import Base
import copy

class Receiver(Base):
    def __init__(self, addr):
        super().__init__()
        self.addr = addr

    def get_blank_receiver(self):
        new_receiver = self.duplicate()
        new_receiver.set_ada(0)
        return new_receiver

    def __str__(self):
        return f'{self.addr}+{self.account}'

    def set_address(self, addr):
        new_recevier = copy.deepcopy(self)
        new_recevier.addr = addr
        return new_recevier
