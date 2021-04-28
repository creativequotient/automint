import json

import automint.utils as utils
import automint.wallet.Wallet as Wallet


if __name__ == '__main__':
    USE_TESTNET = True

    # Query tip
    tip_info = utils.query_tip(use_testnet=USE_TESTNET)
    print(json.dumps(tip_info, indent=4))

    # Query protocol parameters
    protocol_param_fp = utils.get_protocol_params('.', use_testnet=USE_TESTNET)
    with open(protocol_param_fp, 'r') as f:
        params = json.load(f)
        print(json.dumps(params, indent=4))

    # Create wallet
    wallet = Wallet('.', 'test_wallet', use_testnet=USE_TESTNET)
    print(f'Wallet address: {wallet.get_address()}')
    wallet.query_utxo()
    for txHash in wallet.get_utxos():
        utxo = wallet.get_utxo(txHash)
        print(f'txHash: {utxo}')
        print(f'Lovelace: {utxo.get_account().get_lovelace()}')
        print(json.dumps(utxo.get_account().get_native_tokens()))
