import os
import subprocess
import logging
from automint.utxo import UTXO
from automint.config import CARDANO_CLI


logger = logging.getLogger(__name__)


# This class will represent one wallet and support querying of wallet
# details such as utxo-s, signing and verification keys, etc
class Wallet(object):
    def __init__(self, wallet_dir, wallet_name):
        self.name = wallet_name

        # Create wallet directory
        os.makedirs(wallet_dir, exist_ok=True)

        # Define file path for required files this wallet
        self.s_key_fp = os.path.join(wallet_dir, f'{wallet_name}.skey')
        self.v_key_fp = os.path.join(wallet_dir, f'{wallet_name}.vkey')
        self.addr_fp = os.path.join(wallet_dir, f'{wallet_name}.addr')

        # Generate keys as required
        self.set_up()

        # Keep dictionary of UTXOs
        self.UTXOs = {}

    def set_up(self):
        if not os.path.exists(self.s_key_fp) and not os.path.exists(self.v_key_fp):
            logger.info(f'Signing and verification keys for wallet {self.name} not found, generating...')
            proc = subprocess.run([CARDANO_CLI,
                                   'address',
                                   'key-gen',
                                   '--verification-key-file',
                                   self.v_key_fp,
                                   '--signing-key-file',
                                   self.s_key_fp], capture_output=True, text=True)
            if proc.stderr != "":
                logger.error(f'Error encountered when generating wallet keys\n{proc.stderr}')

        if not os.path.exists(self.addr_fp):
            logger.info(f'Address file for wallet {self.name} not found, generating...')
            proc = subprocess.run([CARDANO_CLI,
                                   'address',
                                   'build',
                                   '--payment-verification-key-file',
                                   self.v_key_fp,
                                   '--out-file',
                                   self.addr_fp,
                                   '--mainnet'], capture_output=True, text=True)
            if proc.stderr != "":
                logger.info(f'Error encountered when generating wallet address\n{proc.stderr}')

        assert os.path.exists(self.s_key_fp)
        assert os.path.exists(self.v_key_fp)
        assert os.path.exists(self.addr_fp)

        with open(self.addr_fp, 'r') as addr_f:
            self.addr = addr_f.read().strip()
            addr_f.close()

        # TODO: Check that address is bech32 valid
        assert self.addr != ""

    def query_utxo(self):
        # Query the blockchain for all UTXOs in this wallet
        self.UTXOs = {}

        proc = subprocess.run([CARDANO_CLI,
                               'query',
                               'utxo',
                               '--address',
                               self.addr,
                               '--mainnet'], capture_output=True, text=True)
        if proc.stderr != "":
            logger.info(f'Error encountered when querying UTXO for wallet {self.name}\n{proc.stderr}')

        raw_utxo_str_list = list(filter(lambda x: x != '', proc.stdout.split('\n')[2:]))
        for raw_utxo_str in raw_utxo_str_list:
            utxo = UTXO(raw_utxo_str)
            self.UTXOs.update({
                utxo.get_utxo_identifier(): utxo
            })

        return self.get_utxos()

    def get_utxo(self, identifier=None):
        if identifier is None:
            if len(self.UTXOs) == 0:
                return
            k = list(filter(lambda u: self.UTXOs.get(u).get_account().get_lovelace() > 5000000, self.UTXOs.keys()))
            k = sorted(k, key=lambda u: self.UTXOs.get(u).size())
            if len(k) == 0:
                raise Exception('No UTXO could be selected automatically, please specify via flag')
            return self.UTXOs.get(k[0])

        # Returns the UTXO given the identifier if found, None otherwise
        return self.UTXOs.get(identifier, None)

    def get_utxos(self):
        # Return dictionary of all UTXOs in the wallet
        return self.UTXOs

    def get_skey_path(self):
        return self.s_key_fp

    def get_vkey_path(self):
        return self.v_key_fp

    def get_address(self):
        return self.addr
