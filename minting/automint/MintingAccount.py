from automint.Account import Account
from automint.Base import Base

class MintingAccount(Base):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return f'{self.account}'
