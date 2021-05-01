import os
import json
import logging

from automint.wallet import Wallet
from automint.utils import get_key_hash, write_policy_script_with_time_lock, query_tip, get_policy_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Set up directories
    WORK_DIR = os.path.realpath('.')
    TMP_DIR = os.path.join(WORK_DIR, 'tmp')
    KEYS_DIR = os.path.join(WORK_DIR, 'keys')
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(KEYS_DIR, exist_ok=True)

    # Set up wallets
    payment_wallet = Wallet(KEYS_DIR, 'payment')
    policy_wallet = Wallet(KEYS_DIR, 'policy')

    # Set up policies
    key_hash = get_key_hash(policy_wallet.get_vkey_path())
    current_slot = query_tip()['slot']
    before_slot = current_slot + 60 * 60 * 24 * 7 # This adds 7 days worth of slots from the current slot
    policy_script_fp = write_policy_script_with_time_lock(WORK_DIR, key_hash, before=before_slot)
    policy_id = get_policy_id(policy_script_fp)

    # Write policy id to file
    with open(os.path.join(WORK_DIR, 'policy.id'), 'w') as outfile:
        outfile.write(policy_id)

    logger.info(f'Payment wallet address: {payment_wallet.get_address()}')
    logger.info(f'Policy ID: {policy_id}')
