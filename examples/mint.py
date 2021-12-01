from automint.account import Account
from automint.receivers import TxReceiver
from automint.receivers import MintingReceiver
from automint.wallet import Wallet
from automint.utxo import UTXO
from automint.utils import get_protocol_params, get_policy_id, get_key_hash, write_policy_script, get_policy_id, build_raw_transaction, calculate_tx_fee, submit_transaction, sign_tx
from automint.utils import query_tip
import logging
import os
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    # Set up directories
    WORK_DIR = os.path.realpath('.')
    TMP_DIR = os.path.join(WORK_DIR, 'tmp')
    KEYS_DIR = os.path.join(WORK_DIR, 'keys')

    assert os.path.exists(TMP_DIR)
    assert os.path.exists(KEYS_DIR)

    # Define tokens to be minted
    TOKENS = [f'TestToken{i:02}' for i in range(2)]

    # Define wallets
    # This wallet is for transactions
    payment_wallet = Wallet(KEYS_DIR, 'payment', use_testnet=False)
    # This wallet is ONLY for signing off on the policy to mint tokens
    policy_wallet = Wallet(KEYS_DIR, 'policy', use_testnet=False)
    logger.info(f'Payment wallet address: {payment_wallet.get_address()}')
    logger.info(f'Policy wallet address: {policy_wallet.get_address()}')

    # Query UTXOs at wallet address, this step must be done so that
    # internally, the wallet will become aware of its own UTXOs
    payment_wallet.query_utxo()

    if len(payment_wallet.get_utxos()) <= 0:
        logger.info('No UTXOs found within wallet.')
        logger.info(f'Please send some ADA (~5ADA) to the payment wallet address {payment_wallet.get_address()}')
        exit()

    # Display UTXOs for visual inspection (optional)
    utxo_summary = ''
    for id in payment_wallet.get_utxos():
        utxo = payment_wallet.get_utxo(identifier=id)
        utxo_summary += f'\nUTXO: {utxo}\nADA:: {utxo.get_account().get_ada()}\nContents: {json.dumps(utxo.get_account().native_tokens, indent=4)}'
    logger.info(f'UTXOs found at wallet address...{utxo_summary}')

    # Get UTXO to consume in transaction `payment_wallet.get_utxo()`
    # has some logic to select suitable UTXO to consume based on
    # balance and no. assets currently within the UTXO. In the event
    # that this arbitrary logic fails to find an appropriate UTXO, one
    # can be manually specified by pass the `<txHash>#<index>` to the
    # `get_utxo()` function.
    input_utxo = payment_wallet.get_utxo('013f097180a76fcec4d8e661ec10d2a6be5c6d8b1f866af70caeaaf5d310041e#1')
    logger.info(f'UTXO to be consumed: {input_utxo}')

    # Query blockchain parameters
    protocol_param_fp = get_protocol_params(TMP_DIR, use_testnet=False)
    logger.info(f'Protocol parameters written to {protocol_param_fp}')

    # Acquire policy script and ID
    policy_script_fp = os.path.join(WORK_DIR, 'policy.script')

    with open(os.path.join(WORK_DIR, 'policy.id'), 'r') as f:
        policy_id = f.read().strip()

    logger.info(f'Policy ID: {policy_id}')

    # Create receiver and mintingAccount. Receiver and MintingAccount
    # can conduct arithmetic on the adding / removal of tokens and is
    # used to properly format strings for (--tx-in and --mint fiends)
    # and account for the I/O of the transcation.

    # Converts the UTXO (input_utxo) to Receiver. In this script, we
    # assume that we are minting back into the same wallet and not
    # elsewhere.

    # By changing the argument to `convert_to_receiver`, we can
    # actually sent the contents of the entire UTXO to an arbitrary
    # address. In this sample, we are just sending it back to the
    # minting wallet
    tx_receiver = input_utxo.convert_to_receiver(payment_wallet.get_address())
    minting_receiver = MintingReceiver()
    for token in TOKENS:
        token_id = f'{policy_id}.{token}'

        tx_receiver.remove_native_token(token_id, 1)
        minting_receiver.remove_native_token(token_id, 1)

    receivers = [tx_receiver]

    # Draft transaction with 0 fees. `receiver.get_blank_receiver()`
    # simply returns a clone of the same receiver but with 0 lovelace
    # balance.

    # Note: Specifing the metadata parameter attaches the metadata at
    # the specified location to the transcation. If no metadata is to
    # be added, simply omit the argument.

    invalid_after_slot = query_tip(use_testnet=False)['slot'] + 3600

    raw_matx_path = build_raw_transaction(TMP_DIR,
                                          input_utxo,
                                          receivers,
                                          minting_receiver,
                                          invalid_after=invalid_after_slot,
                                          minting_script=policy_script_fp)
    logger.info(f'Draft transaction written to {raw_matx_path}...')

    # Caculate fees
    fee = calculate_tx_fee(raw_matx_path, protocol_param_fp, input_utxo, receivers, use_testnet=True)
    fee = int(fee * 2)
    logger.info(f'Calculated transaction fee: {fee} lovelace')

    # Adjust fees in lovelace in receiver
    tx_receiver.remove_lovelace(fee)

    # Draft transaction but with fees accounted for
    raw_matx_path = build_raw_transaction(TMP_DIR,
                                          input_utxo,
                                          receivers,
                                          minting_receiver,
                                          fee=fee,
                                          invalid_after=invalid_after_slot,
                                          minting_script=policy_script_fp)
    logger.info(f'Draft transaction with fees written to {raw_matx_path}...')

    # Sign transaction
    signed_matx_path = sign_tx(TMP_DIR,
                               [payment_wallet, policy_wallet],
                               raw_matx_path,
                               use_testnet=False)
    logger.info(f'Signed transaction written to {signed_matx_path}')

    # Submit transaction to the blockchain
    result = submit_transaction(signed_matx_path, use_testnet=False)
    if result:
        logger.info(f'Successfully submitted transaction!')
    else:
        logger.info(f'Failed to submit transaction')
