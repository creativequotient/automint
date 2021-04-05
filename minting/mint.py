import subprocess
import os


def generate_keys(nft_dir, name):
    """Generate signing and verification keys and returns their location"""
    assert name in ['policy', 'payment']
    vkey_path = os.path.join(nft_dir, f'{name}.vkey')
    skey_path = os.path.join(nft_dir, f'{name}.skey')
    proc = subprocess.run(['cardano-cli',
                           'address',
                           'key-gen',
                           '--verification-key-file',
                           vkey_path,
                           '--signing-key-file',
                           skey_path], capture_output=True, text=True)
    return {'vkey_path': vkey_path, 'skey_path': skey_path}


def build_address(nft_dir):
    """Create address given verification key"""
    vkey_path = os.path.join(nft_dir, 'payment.vkey')
    addr_path = os.path.join(nft_dir, 'payment.addr')
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
    return {'vkey_path': vkey_path, 'addr_path': addr_path, 'addr': addr}


def query_utxo(addr):
    """Query utxo of a given address"""
    proc = subprocess.run(['cardano-cli',
                           'query',
                           'utxo',
                           '--address',
                           addr,
                           '--mainnet',
                           '--mary-era'], capture_output=True, text=True)
    return proc.stdout.decode('utf-8')


def query_protocol_parameters(nft_dir):
    """Query protocol parameters"""
    protocol_json_path = os.path.join(nft_dir, 'protocol.json')
    proc = subprocess.run(['cardano-cli',
                           'query',
                           'protocol-parameters',
                           '--mainnet',
                           '--out-file',
                           protocol_json_path], capture_output=True, text=True)
    return {'protocol_json_path': protocol_json_path}


def get_key_hash(policy_vkey):
    """Generate and return key hash given policy verification key"""
    proc = subprocess.run(['cardano-cli',
                           'address',
                           'key-hash',
                           '--payment-verification-key-file',
                           policy_vkey], capture_output=True, text=True)
    return proc.stdout.decode('utf-8')


def make_policy_script(nft_dir, policy_vkey):
    """Format string representation of policy script"""
    return f'{"keyHash": f{policy_vkey}, "type": "sig"}'


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
    return proc.stdout.decode('utf-8')


def build_raw_tranaction(nft_dir, tx_hash, payment_addr, policy_id, tokens, fee=0):
    """Builds transactions"""
    assert type(tokens) == list

    def token_mint_formatted():
        tokens_w_policy = list(map(lambda token: f'1 {policy_id}.{token}', tokens))
        return ' + '.join(tokens_w_policy)

    raw_matx_path = os.path.join(nft_dir, 'matx.raw')

    proc = subprocess.run(['cardano-cli',
                           'transaction',
                           'build-raw',
                           '--mary-era',
                           '--tx-in',
                           f'{tx_hash}#0',
                           '--tx-out',
                           f'{payment_addr}+{fee}+"{token_mint_formatted()}"',
                           '--mint',
                           token_mint_formatted(),
                           '--out-file',
                           raw_matx_path], capture_output=True, text=True)
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
    return int(proc.stdout.decode('utf-8').split()[0])


def sign_tx(nft_dir, payment_skey_path, policy_skey_path, policy_script_path, raw_matx_path):
    """Generate and write signed transaction file"""
    signed_matx_path = os.path.join(nft_dir, 'matx.signed')
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
    return {'signed_matx_path': signed_matx_path}


def submit_transaction(signed_matx_path):
    """Submit signed transaction"""
    proc = subprocess.run(['cardano-cli',
                           'transaction',
                           'submit',
                           '--tx-file',
                           signed_matx_path,
                           '--mainnet'], capture_output=True, text=True)
    return proc.stdout.decode('utf-8')
