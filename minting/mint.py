import subprocess
import os
import pprint


def generate_keys(nft_dir, name, force=False):
    """Generate signing and verification keys and returns their location"""

    assert name in ['policy', 'payment']

    vkey_path = os.path.join(nft_dir, f'{name}.vkey')
    skey_path = os.path.join(nft_dir, f'{name}.skey')

    # Only generate/overwrite the keys if they do not exist or force=True
    if force or not os.path.exists(vkey_path) or not os.path.exists(skey_path):
        proc = subprocess.run(['cardano-cli',
                               'address',
                               'key-gen',
                               '--verification-key-file',
                               vkey_path,
                               '--signing-key-file',
                               skey_path], capture_output=True, text=True)

    return {f'{name}_vkey_path': vkey_path, f'{name}_skey_path': skey_path}


def build_address(nft_dir, force=False):
    """Create address given verification key"""

    vkey_path = os.path.join(nft_dir, 'payment.vkey')
    addr_path = os.path.join(nft_dir, 'payment.addr')

    # Only generate/overwrite the address if it does not exist or force=True
    if force or not os.path.exists(addr_path):
        proc = subprocess.run(['cardano-cli',
                               'address',
                               'build',
                               '--payment-verification-key-file',
                               vkey_path,
                               '--out-file',
                               addr_path,
                               '--mainnet'], capture_output=True, text=True)

    with open(addr_path, 'r') as addr_file:
        addr = addr_file.read()
        addr_file.close()

    return {'payment_vkey_path': vkey_path, f'addr_path': addr_path, 'addr': addr}


def query_utxo(addr):
    """Query utxo of a given address"""

    # Ensure that address is valid
    assert len(addr) > 0

    proc = subprocess.run(['cardano-cli',
                           'query',
                           'utxo',
                           '--address',
                           addr,
                           '--mainnet',
                           '--mary-era'], capture_output=True, text=True)

    # The following filter removes the headers of the UTxO output
    return list(filter(lambda x: x != '', proc.stdout.split('\n')[2:]))


def query_protocol_parameters(nft_dir, force=False):
    """Query protocol parameters"""

    protocol_json_path = os.path.join(nft_dir, 'protocol.json')

    # Only generate/overwrite the protocol.json if it does not exist or force=True
    if force or not os.path.exists(protocol_json_path):
        proc = subprocess.run(['cardano-cli',
                               'query',
                               'protocol-parameters',
                               '--mainnet',
                               '--mary-era',
                               '--out-file',
                               protocol_json_path], capture_output=True, text=True)
        print(proc.stdout)

    return {'protocol_json_path': protocol_json_path}


def get_key_hash(policy_vkey):
    """Generate and return key hash given policy verification key"""

    if not os.path.exists(policy_vkey):
        raise Exception(f'Policy verification key file {policy_vkey} does not exists.')

    proc = subprocess.run(['cardano-cli',
                           'address',
                           'key-hash',
                           '--payment-verification-key-file',
                           policy_vkey], capture_output=True, text=True)
    return proc.stdout.strip('\n')


def make_policy_script(nft_dir, key_hash):
    """Format string representation of policy script"""
    return '{\n  "keyHash": "' + key_hash + '",\n  "type": "sig"\n}'


def write_policy_script(nft_dir, script):
    """Write policy script to file and return location"""
    script_path = os.path.join(nft_dir, 'policy.script')
    with open(script_path, 'w') as script_file:
        script_file.write(script)
        script_file.close()
    return {'policy_script_path': script_path}


def get_policy_id(policy_script_path):
    """Return policy id given policy script"""
    proc = subprocess.run(['cardano-cli',
                           'transaction',
                           'policyid',
                           '--script-file',
                           policy_script_path], capture_output=True, text=True)
    return proc.stdout.strip('\n')


def build_raw_transaction(nft_dir, tx_hash, payment_addr, policy_id, tokens, fee=0, out_amt=0, force=False):
    """Builds transactions"""
    assert type(tokens) == list

    def format_assets():
        """Helper function to format native asset tx strings"""
        tokens_w_policy = list(map(lambda token: f'1 {policy_id}.{token}', tokens))
        return '\"' + ' + '.join(tokens_w_policy) + '\"'

    raw_matx_path = os.path.join(nft_dir, 'matx.raw')

    # Only generate/overwrite the keys if they do not exist or force=True
    if force or not os.path.exists(raw_matx_path):
        cmd = " ".join(['cardano-cli',
                        'transaction',
                        'build-raw',
                        '--mary-era',
                        '--fee',
                        f'{fee}',
                        '--tx-in',
                        f'{tx_hash}',
                        '--tx-out',
                        f'{payment_addr}+{out_amt}+{format_assets()}',
                        '--mint',
                        format_assets(),
                        '--out-file',
                        raw_matx_path])

        proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        # print(f'{payment_addr}+{fee}+{format_assets()}')
        # print(cmd)
        # print(proc.stdout)
        print(proc.stderr)

    return {'raw_matx_path': raw_matx_path}


def calculate_tx_fees(raw_matx_path, protocol_json_path):
    """Calculate transaction fees"""
    proc = subprocess.run(['cardano-cli',
                           'transaction',
                           'calculate-min-fee',
                           '--tx-body-file',
                           raw_matx_path,
                           '--tx-in-count',
                           '1',
                           '--tx-out-count',
                           '1',
                           '--witness-count',
                           '2',
                           '--mainnet',
                           '--protocol-params-file',
                           protocol_json_path], capture_output=True, text=True)
    return int(proc.stdout.split()[0])


def sign_tx(nft_dir, payment_skey_path, policy_skey_path, policy_script_path, raw_matx_path, force=False):
    """Generate and write signed transaction file"""
    signed_matx_path = os.path.join(nft_dir, 'matx.signed')

    # Only generate/overwrite the keys if they do not exist or force=True
    if force or not os.path.exists(signed_matx_path):
        proc = subprocess.run(['cardano-cli',
                               'transaction',
                               'sign',
                               '--signing-key-file',
                               payment_skey_path,
                               '--signing-key-file',
                               policy_skey_path,
                               '--script-file',
                               policy_script_path,
                               '--mainnet',
                               '--tx-body-file',
                               raw_matx_path,
                               '--out-file',
                               signed_matx_path], capture_output=True, text=True)

        print(proc.stdout)

    return {'signed_matx_path': signed_matx_path}


def submit_transaction(signed_matx_path):
    """Submit signed transaction"""

    proc = subprocess.run(['cardano-cli',
                           'transaction',
                           'submit',
                           '--tx-file',
                           signed_matx_path,
                           '--mainnet'], capture_output=True, text=True)

    print(proc.stdout)

    return proc.stdout


def user_confirmation(message, func, **kwargs):
    print(message)
    print(func(**kwargs))
    while input('Enter "Y" to confirm and proceed ') != 'Y':
        print(func(**kwargs))


if __name__ == '__main__':
    DIR = os.path.realpath('temp2')
    FORCE = False
    TOKENS = ['sampleToken01', 'sampleToken02']

    # Obtain payment keys
    info = generate_keys(DIR, 'payment', force=FORCE)

    # Obtain payment address
    info.update(build_address(DIR, force=FORCE))

    # Wait for deposit
    user_confirmation(f'Confirm that ADA has been deposited to the following address before proceeding: {info["addr"]}',
                      query_utxo,
                      addr=info['addr'])

    # TODO: generate txHash, this is just a placeholder
    txHash = '7071b34d10808a1c5963086d0364275119684b3230fa235ac23f7af3afe57bd4#0'
    deposited_amt = 5000000
    info.update({'txHash': txHash,
                 'deposited_amt': deposited_amt})

    # Query protocol parameters
    info.update(query_protocol_parameters(DIR, force=FORCE))

    # Obtain policy keys
    info.update(generate_keys(DIR, 'policy', force=FORCE))

    # Create policy script
    key_hash = get_key_hash(info['policy_vkey_path'])
    script = make_policy_script(DIR, key_hash)
    info.update(write_policy_script(DIR, script))
    info.update({'policy': get_policy_id(info['policy_script_path'])})

    print(f'key_hash: {key_hash}')
    print(f'policy: {info["policy"]}')

    # Build empty transaction to calculate fees
    info.update(build_raw_transaction(DIR,
                                      info['txHash'],
                                      info['addr'],
                                      info['policy'],
                                      TOKENS,
                                      fee=0,
                                      force=FORCE))
    tx_fee = calculate_tx_fees(info['raw_matx_path'], info['protocol_json_path'])
    unspent_amt = info['deposited_amt'] - tx_fee
    info.update({'tx_fee': tx_fee,
                 'unspent_amt': unspent_amt})

    # Build transaction again but with fees
    info.update(build_raw_transaction(DIR,
                                      info['txHash'],
                                      info['addr'],
                                      info['policy'],
                                      TOKENS,
                                      fee=info['tx_fee'],
                                      out_amt=info['unspent_amt'],
                                      force=FORCE))

    # Sign transaction
    info.update(sign_tx(DIR,
                        info['payment_skey_path'],
                        info['policy_skey_path'],
                        info['policy_script_path'],
                        info['raw_matx_path'],
                        force=False))

    # Submit transaction
    submit_transaction(info['signed_matx_path'])

    # Confirm NFTs minted
    user_confirmation(f'Confirm that the new assets have been deposited',
                      query_utxo,
                      addr=info['addr'])

    pprint.PrettyPrinter(indent=4, depth=6).pprint(info)
