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
        return ""

    return protocol_json_path


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

def build_raw_transaction(working_dir, input_utxos, output_accounts, policy_id=None,  minting_account=None, fee=0, metadata=None):
    """Builds transactions"""

    if type(input_utxos) != list:
        input_utxos = [input_utxos]

    if type(output_accounts) != list:
        output_accounts = [output_accounts]

    raw_matx_path = os.path.join(working_dir, 'matx.raw')

    # Only generate/overwrite the keys if they do not exist or force=True
    cmd_builder  = [CARDANO_CLI.replace(' ', '\ '),
                    'transaction',
                    'build-raw',
                    '--mary-era',
                    '--fee',
                    f'{fee}',
                    '--out-file',
                    raw_matx_path]

    for utxo in input_utxos:
        cmd_builder.append('--tx-in')
        cmd_builder.append(str(utxo))

    for acc in output_accounts:
        cmd_builder.append('--tx-out')
        cmd_builder.append(str(acc))

    if minting_account:
        cmd_builder.append(f'--mint={minting_account}')

    if metadata:
        cmd_builder.append('--metadata-json-file')
        cmd_builder.append(metadata)

    cmd = " ".join(cmd_builder)

    logging.info(f'Transaction build command:\n{cmd}')
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if proc.stderr != "":
        logging.info(f'Error encountered when building transaction\n{cmd_builder}\n{proc.stderr}')

    return raw_matx_path


def calculate_tx_fee(raw_matx_path, protocol_json_path, input_utxos, output_accounts):
    """Calculate transaction fees"""

    if type(input_utxos) != list:
        input_utxos = [input_utxos]

    if type(output_accounts) != list:
        output_accounts = [output_accounts]

    proc = subprocess.run([CARDANO_CLI,
                           'transaction',
                           'calculate-min-fee',
                           '--tx-body-file',
                           raw_matx_path,
                           '--tx-in-count',
                           f'{len(input_utxos)}',
                           '--tx-out-count',
                           f'{len(output_accounts)}',
                           '--witness-count',
                           '2',
                           '--mainnet',
                           '--protocol-params-file',
                           protocol_json_path], capture_output=True, text=True)

    if proc.stderr != '':
        logging.info(f'Error encountered when calculating transcation fee...\n{proc.stdout}')
        logging.info(f'{proc.stderr}')

    return int(proc.stdout.split()[0])


def sign_tx(nft_dir, signing_wallets, raw_matx_path, script_path=None, force=False):
    """Generate and write signed transaction file"""
    if type(signing_wallets) != list:
        signing_wallets = [signing_wallets]

    signed_matx_path = os.path.join(nft_dir, 'matx.signed')

    # Only generate/overwrite the keys if they do not exist or force=True
    cmd_builder = [CARDANO_CLI.replace(' ', '\ '),
                    'transaction',
                    'sign',
                    '--mainnet',
                    '--tx-body-file',
                    raw_matx_path,
                    '--out-file',
                    signed_matx_path]

    for wallet in signing_wallets:
        cmd_builder.append('--signing-key-file')
        cmd_builder.append(wallet.get_skey_path())

    if script_path:
        cmd_builder.append('--script-file')
        cmd_builder.append(script_path)

    cmd = ' '.join(cmd_builder)

    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if proc.stderr != '':
        logging.info(f'Error encountered when signing transaction\n{proc.stderr}')

    return signed_matx_path


def submit_transaction(signed_matx_path):
    """Submit signed transaction"""

    proc = subprocess.run([CARDANO_CLI,
                           'transaction',
                           'submit',
                           '--tx-file',
                           signed_matx_path,
                           '--mainnet'], capture_output=True, text=True)

    if proc.stderr != '':
        logging.info(f'Error encountered when submitting transaction\n{proc.stderr}')
        return False
    logging.info(f'{proc.stdout}')
    return True
