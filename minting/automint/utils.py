import subprocess
import os
import logging
import json
from automint.config import CARDANO_CLI

logging.basicConfig(level=logging.INFO)


def get_protocol_params(working_dir):
    """Query protocol parameters and write to file"""

    protocol_json_path = os.path.join(working_dir, 'protocol.json')

    proc = subprocess.run([CARDANO_CLI,
                           'query',
                           'protocol-parameters',
                           '--mainnet',
                           '--mary-era',
                           '--out-file',
                           protocol_json_path], capture_output=True, text=True)

    if proc.stderr != "":
        logging.info(f'Failed to fetch protocol parameters...')
        return False

    return True


def get_key_hash(policy_vkey_path):
    """Generate and return key hash given policy verification key"""

    if not os.path.exists(policy_vkey_path):
        raise Exception(f'Policy verification key file {policy_vkey} does not exists.')

    proc = subprocess.run([CARDANO_CLI,
                           'address',
                           'key-hash',
                           '--payment-verification-key-file',
                           policy_vkey_path], capture_output=True, text=True)

    if proc.stderr != "":
        logging.info(f'Failed to compute keyHash')

    return proc.stdout.strip('\n')


def write_policy_script(working_dir, keyHash, force=False):
    """Write policy script to file and return location"""
    script_path = os.path.join(working_dir, 'policy.script')

    if force or not os.path.exists(script_path):
        logging.info(f'Writing policy script to {script_path}')
        with open(script_path, 'w') as script_f:
            json.dump({
                'keyHash': keyHash,
                'type': 'sig'
            }, script_f, indent=4)
            script_f.close()

    return script_path


def get_policy_id(policy_script_path):
    """Return policy id given policy script"""
    proc = subprocess.run([CARDANO_CLI,
                           'transaction',
                           'policyid',
                           '--script-file',
                           policy_script_path], capture_output=True, text=True)
    return proc.stdout.strip('\n')
