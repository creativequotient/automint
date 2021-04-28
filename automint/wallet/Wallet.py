import os
import subprocess
import logging
from automint.utxo import UTXO
from automint.config import CARDANO_CLI, TESTNET_MAGIC_DEFAULT


logger = logging.getLogger(__name__)


class Wallet(object):
    def __init__(self, wallet_dir, wallet_name, use_testnet=False, testnet_magic=TESTNET_MAGIC_DEFAULT):
        '''
        This class will represent one wallet and support querying of wallet
        details such as utxos, locating of signing and verification keys, etc
        '''
        self.name = wallet_name
        self.use_testnet = use_testnet
        self.testnet_magic = testnet_magic

        # Define file path for required files this wallet
        self.s_key_fp = os.path.join(wallet_dir, f'{wallet_name}.skey')
        self.v_key_fp = os.path.join(wallet_dir, f'{wallet_name}.vkey')
        self.addr_fp = os.path.join(wallet_dir, f'{wallet_name}.addr')

        # Generate keys as required
        self.set_up(wallet_dir)

        # Keep dictionary of UTXOs
        self.UTXOs = {}

    def set_up(self, wallet_dir):
        if not os.path.exists(wallet_dir):
            # Create wallet directory if does not exist
            logger.info(f'{wallet_dir} does not exist, creating directory...')
            os.makedirs(wallet_dir, exist_ok=True)

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

            cmd_builder = [CARDANO_CLI.replace(' ', '\ '),
                           'address',
                           'build',
                           '--payment-verification-key-file',
                           self.v_key_fp,
                           '--out-file',
                           self.addr_fp]

            if self.use_testnet:
                cmd_builder.append('--testnet-magic')
                cmd_builder.append(str(self.testnet_magic))
            else:
                cmd_builder.append('--mainnet')

            cmd = ' '.join(cmd_builder)

            proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

            if proc.stderr != '':
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
        '''Query the blockchain for all UTXOs at the wallet address'''
        self.UTXOs = {}

        cmd_builder = [CARDANO_CLI,
                       'query',
                       'utxo',
                       '--address',
                       self.addr]

        if self.use_testnet:
            cmd_builder.append('--testnet-magic')
            cmd_builder.append(str(self.testnet_magic))
        else:
            cmd_builder.append('--mainnet')

        cmd = ' '.join(cmd_builder)

        proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        if proc.stderr != '':
            logger.info(f'Error encountered when querying UTXO for wallet {self.name}\n{proc.stderr}')

        raw_utxo_str_list = list(filter(lambda x: x != '', proc.stdout.split('\n')[2:]))
        for raw_utxo_str in raw_utxo_str_list:
            utxo = UTXO(raw_utxo_str)
            self.UTXOs.update({
                utxo.get_utxo_identifier(): utxo
            })

        return self.get_utxos()

    def get_utxo(self, identifier=None):
        '''Returns UTXO specified by identifier if provided, otherwise, returns arbitrary UTXO'''
        if identifier is None:
            if len(self.UTXOs) == 0:
                return None

            # Automatically select UTXOs with more than 2000000 lovelace and smallest size
            valid_utxos = list(filter(lambda u: self.UTXOs.get(u).get_account().get_lovelace() >= 2000000, self.UTXOs.keys()))
            valid_utxos = sorted(valid_utxos, key=lambda u: self.UTXOs.get(u).size())

            if len(valid_utxos) == 0:
                # No UTXO remaining after filtering
                raise Exception('No UTXO could be selected automatically, please specify via identfier named argument')

            return self.UTXOs.get(valid_utxos[0])

        # Returns the UTXO given the identifier if found, None otherwise
        return self.UTXOs.get(identifier, None)

    def get_utxos(self):
        '''Return all UTXOs within Wallet as a dictionary indexed by txHash'''
        return self.UTXOs

    def get_skey_path(self):
        '''Return filepath to signing key'''
        return self.s_key_fp

    def get_vkey_path(self):
        '''Return filepath to verification key'''
        return self.v_key_fp

    def get_address(self):
        '''Return address of wallet'''
        return self.addr

    def __str__(self):
        '''Return string representation of wallet which is its address'''
        return self.get_address()
