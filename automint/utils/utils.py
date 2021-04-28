import subprocess
import os
import logging
import json
import requests
from automint.config import CARDANO_CLI, TESTNET_MAGIC_DEFAULT


logger = logging.getLogger(__name__)


def get_protocol_params(working_dir, use_testnet=False, testnet_magic=TESTNET_MAGIC_DEFAULT):
    """Query protocol parameters and write to file"""

    protocol_json_path = os.path.join(working_dir, 'protocol.json')

    cmd_builder = [CARDANO_CLI.replace(' ', '\ '),
                   'query',
                   'protocol-parameters',
                   '--out-file',
                   protocol_json_path]

    if use_testnet:
        cmd_builder.append('--testnet-magic')
        cmd_builder.append(str(testnet_magic))
    else:
        cmd_builder.append('--mainnet')

    cmd = ' '.join(cmd_builder)

    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if proc.stderr != '':
        logger.error(f'Failed to fetch protocol parameters...')
        return ''

    return protocol_json_path


def get_key_hash(policy_vkey_path):
    """Generate and return key hash given policy verification key"""

    if not os.path.exists(policy_vkey_path):
        raise Exception(f'Policy verification key file expected at {policy_vkey_path} does not exists.')

    proc = subprocess.run([CARDANO_CLI,
                           'address',
                           'key-hash',
                           '--payment-verification-key-file',
                           policy_vkey_path], capture_output=True, text=True)

    if proc.stderr != "":
        logger.error(f'Failed to compute keyHash')

    return proc.stdout.strip('\n')


def write_policy_script(working_dir, keyHash, force=False):
    """Write policy script to file and return location"""
    script_path = os.path.join(working_dir, 'policy.script')

    if force or not os.path.exists(script_path):
        logger.info(f'Writing policy script to {script_path}')
        with open(script_path, 'w') as script_f:
            json.dump({
                'keyHash': keyHash,
                'type': 'sig'
            }, script_f, indent=4)
            script_f.close()

    return script_path


def write_policy_script_with_time_lock(working_dir, keyHash, before, force=False):
    """Write policy script to file and return location"""
    script_path = os.path.join(working_dir, 'policy.script')

    if force or not os.path.exists(script_path):
        logger.info(f'Writing policy script to {script_path}')
        with open(script_path, 'w') as script_f:
            json.dump({
                'type': 'all',
                'scripts':[{
                    'keyHash': keyHash,
                    'type': 'sig'
                },{
                    'slot': before,
                    'type': 'before'
                }]
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


def build_raw_transaction(working_dir, input_utxos, output_accounts, policy_id=None,  minting_account=None, fee=0, metadata=None, invalid_after=None, script_path=None):
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

    if invalid_after:

        assert type(invalid_after) == int
        cmd_builder.append('--invalid-hereafter')
        cmd_builder.append(str(invalid_after))

    if minting_account:
        cmd_builder.append('--minting-script-file')
        cmd_builder.append(script_path)

    cmd = " ".join(cmd_builder)

    logger.debug(f'Transaction build command:\n{cmd}')

    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if proc.stderr != '':
        logger.error(f'Error encountered when building transaction\n{cmd_builder}\n{proc.stderr}')

    return raw_matx_path


def calculate_tx_fee(raw_matx_path, protocol_json_path, input_utxos, output_accounts, witness_count=2, use_testnet=False, testnet_magic=TESTNET_MAGIC_DEFAULT):
    """Calculate transaction fees"""

    if type(input_utxos) != list:
        input_utxos = [input_utxos]

    if type(output_accounts) != list:
        output_accounts = [output_accounts]

    assert witness_count >= len(input_utxos)

    cmd_builder = [CARDANO_CLI.replace(' ', '\ '),
                 'transaction',
                 'calculate-min-fee',
                 '--tx-body-file',
                 raw_matx_path,
                 '--tx-in-count',
                 f'{len(input_utxos)}',
                 '--tx-out-count',
                 f'{len(output_accounts)}',
                 '--witness-count',
                 f'{witness_count}',
                 '--protocol-params-file',
                 protocol_json_path]

    if use_testnet:
        cmd_builder.append('--testnet-magic')
        cmd_builder.append(str(testnet_magic))
    else:
        cmd_builder.append('--mainnet')

    cmd = ' '.join(cmd_builder)

    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if proc.stderr != '':
        logger.error(f'Error encountered when calculating transcation fee...\n{proc.stdout}')
        logger.debug(f'{proc.stderr}')
        return ''

    return int(proc.stdout.split()[0])


def sign_tx(nft_dir, signing_wallets, raw_matx_path, force=False, use_testnet=False, testnet_magic=TESTNET_MAGIC_DEFAULT):
    """Generate and write signed transaction file"""
    if type(signing_wallets) != list:
        signing_wallets = [signing_wallets]

    signed_matx_path = os.path.join(nft_dir, 'matx.signed')

    # Only generate/overwrite the keys if they do not exist or force=True
    cmd_builder = [CARDANO_CLI.replace(' ', '\ '),
                   'transaction',
                   'sign',
                   '--tx-body-file',
                   raw_matx_path,
                   '--out-file',
                   signed_matx_path]

    for wallet in signing_wallets:
        cmd_builder.append('--signing-key-file')
        cmd_builder.append(wallet.get_skey_path())

    if use_testnet:
        cmd_builder.append('--testnet-magic')
        cmd_builder.append(str(testnet_magic))
    else:
        cmd_builder.append('--mainnet')

    cmd = ' '.join(cmd_builder)

    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if proc.stderr != '':
        logger.error(f'Error encountered when signing transaction\n{proc.stderr}')
        return ''

    return signed_matx_path


def submit_transaction(signed_matx_path, use_testnet=False, testnet_magic=TESTNET_MAGIC_DEFAULT):
    """Submit signed transaction"""

    cmd_builder = [CARDANO_CLI.replace(' ', '\ '),
                   'transaction',
                   'submit',
                   '--tx-file',
                   signed_matx_path]

    if use_testnet:
        cmd_builder.append('--testnet-magic')
        cmd_builder.append(str(testnet_magic))
    else:
        cmd_builder.append('--mainnet')

    cmd = ' '.join(cmd_builder)

    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if proc.stderr != '':
        logger.error(f'Error encountered when submitting transaction\n{proc.stderr}')
        return False

    logger.debug(f'{proc.stdout}')

    return True


def get_return_address_from_utxo(utxo):
    try:
        r = requests.get(f"https://cardanoscan.io/transaction/{utxo}")

        content = r.content.decode("utf-8").split(
            'FROM ADDRESSES (INPUTS)</span></div></div><div class=mt-4><div class="d-flex flex-row '
            'justify-content-between px-3"><div><strong>Address</strong></div><div><strong>Amount</strong></div></div><hr class=darkHR><div data-simplebar><div class="d-flex flex-row justify-content-between px-2"><div class=addressField><div class="row align-items-center"><div class=col-auto>')
        sub = content[1].split("span")
        address = sub[0]
        address = address.replace("<a href=/address/", "").replace("><", "")
        return address
    except requests.exceptions.RequestException as e:
        return ''


def get_stake_key(address):
    try:
        req = requests.get(f"https://cardanoscan.io/address/{address}")

        return req.content.decode("utf-8").split('<strong>')[2].split('</strong')[0]

    except requests.exceptions.RequestException as e:
        logger.error(f'Unable to acquire stake key for {address}')
        return ""


def get_cli_version():
    proc = subprocess.run([CARDANO_CLI,
                           '--version'], capture_output=True, text=True,)

    if proc.stderr != '':
        logger.error('Unable to get version')
        return ''

    return proc.stdout.split()[1]


def query_tip(use_testnet=False, testnet_magic=TESTNET_MAGIC_DEFAULT):
    cmd_builder = [CARDANO_CLI,
                   'query',
                   'tip']

    if use_testnet:
        cmd_builder.append('--testnet-magic')
        cmd_builder.append(str(testnet_magic))
    else:
        cmd_builder.append('--mainnet')

    cmd = ' '.join(cmd_builder)

    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if proc.stderr != '':
        logger.error('Unable to query tip information')
        return {}

    return json.loads(proc.stdout)
