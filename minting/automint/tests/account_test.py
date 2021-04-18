from automint.Account import Account

if __name__ == '__main__':

    # Account A
    account_a = Account()
    account_a = account_a.add_ada(5)
    account_a = account_a.add_lovelace(1000000)
    account_a = account_a.add_native_token('12345.sampleAsset01',1)
    account_a = account_a.add_native_token('12345.sampleAsset02',1)
    account_a = account_a.add_native_token('12345.sampleAsset03',1)
    print(account_a)

    # Account B
    account_b = Account()
    account_b = account_b.add_ada(10)
    account_b = account_b.remove_ada(5)
    account_b = account_b.add_native_token('12345.sampleAsset01', 1)
    account_b = account_b.remove_native_token('12345.sampleAsset01', 1)
    print(account_b)
