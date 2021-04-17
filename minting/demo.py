
from automint.Account import Account
from automint.Wallet import Wallet
from automint.UTXO import UTXO
from automint.utils import get_protocol_params, get_policy_id, get_key_hash, write_policy_script, get_policy_id
import logging
import os

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    NFT_DIR = os.path.realpath('demo_nft')

    # Create wallets
    payment_wallet = Wallet(NFT_DIR, 'payment')
    policy_wallet = Wallet(NFT_DIR, 'policy')

    # Query UTXO
    payment_wallet.query_utxo()

    # Display UTXOs
    logging.info(payment_wallet.get_utxos())

    # Get UTXO to consume
    input_utxo = payment_wallet.get_utxo()
    logging.info(f'UTXO to be consumed: {input_utxo}')

    # Get protocol param
    protocol_param_fp = get_protocol_params(NFT_DIR)
    logging.info(f'Protocl parameters written to {protocol_param_fp}')

    # Get keyHash
    key_hash = get_key_hash(policy_wallet.get_vkey_path())
    logging.info(f'keyHash generated...')

    # Write policy script
    policy_script_fp = write_policy_script(NFT_DIR, key_hash, force=False)
    logging.info(f'Policy script found at {policy_script_fp}...')

    # Get policy_id
    policy_id = get_policy_id(policy_script_fp)
    logging.info(f'Policy id: {policy_id}')
