from automint.Account import Account
from automint.Receiver import Receiver
from automint.MintingAccount import MintingAccount
from automint.Wallet import Wallet
from automint.UTXO import UTXO
from automint.utils import get_protocol_params, get_policy_id, get_key_hash, write_policy_script, get_policy_id, build_raw_transaction, calculate_tx_fee, submit_transaction, sign_tx
import logging
import os

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    # Initial set-up
    NFT_DIR = os.path.realpath('bobabits_nft')

    TEMP_DIR = os.path.join(NFT_DIR, 'tmp')
    os.makedirs(TEMP_DIR, exist_ok=True)

    METADATA_FP = os.path.join(NFT_DIR, 'metadata.json')

    # Define tokens to be minted
    TOKENS = [f'sampleToken{i:02}' for i in range(20)]

    # Define wallets
    payment_wallet = Wallet(NFT_DIR, 'payment') # This wallet is for transactions
    policy_wallet = Wallet(NFT_DIR, 'policy') # This wallet is ONLY for signing off on the policy to mint tokens
    logging.info(f'Payment wallet address: {payment_wallet.get_address()}')
    logging.info(f'Policy wallet address: {policy_wallet.get_address()}')

    # Query UTXOs at wallet address, this step must be done so that
    # internally, the wallet will become aware of its own UTXOs
    payment_wallet.query_utxo()

    # Display UTXOs for visual inspection (optional)
    utxo_summary = ''
    for id in payment_wallet.get_utxos():
        utxo = payment_wallet.get_utxo(identifier=id)
        utxo_summary += f'\nUTXO: {utxo}\nContents: {utxo.get_account()}'
    logging.info(f'UTXOs found at wallet address...{utxo_summary}')

    # Get UTXO to consume in transaction `payment_wallet.get_utxo()`
    # has some logic to select suitable UTXO to consume based on
    # balance and no. assets currently within the UTXO. In the event
    # that this arbitrary logic fails to find an appropriate UTXO, one
    # can be manually specified by pass the `<txHash>#<index>` to the
    # `get_utxo()` function.
    input_utxo = payment_wallet.get_utxo()
    logging.info(f'UTXO to be consumed: {input_utxo}')

    # Query blockchain parameters
    protocol_param_fp = get_protocol_params(TEMP_DIR)
    logging.info(f'Protocol parameters written to {protocol_param_fp}')

    # Compute keyHash (may be redundant if policy.script already
    # exists since a new policy.script will not be regenerated and
    # hence, no need to compute this)
    key_hash = get_key_hash(policy_wallet.get_vkey_path())
    logging.info(f'keyHash generated...')

    # Generate policy script if it does not already exist at
    # `NFT_DIR/policy.script`
    policy_script_fp = write_policy_script(NFT_DIR, key_hash, force=False)
    logging.info(f'Policy script found at {policy_script_fp}...')

    # Generate policy_id
    policy_id = get_policy_id(policy_script_fp)
    logging.info(f'Policy id: {policy_id}')

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
    receiver = input_utxo.convert_to_receiver(payment_wallet.get_address())
    minting_account = MintingAccount()
    for token in TOKENS:
        token_id = f'{policy_id}.{token}'
        # Add/remove tokens from the receiver and minting_account
        # (since tokens will be minted/burned)

        receiver.add_native_token(token_id, 1)
        minting_account.add_native_token(token_id, 1)
        # receiver.remove_native_token(token_id, 1)
        # minting_account.remove_native_token(token_id, 1)

    # Draft transaction with 0 fees. `receiver.get_blank_receiver()`
    # simply returns a clone of the same receiver but with 0 lovelace
    # balance.

    # Note: Specifing the metadata parameter attaches the metadata at
    # the specified location to the transcation. If no metadata is to
    # be added, simply omit the argument.
    raw_matx_path = build_raw_transaction(TEMP_DIR,
                                          input_utxo,
                                          receiver.get_blank_receiver(),
                                          policy_id,
                                          minting_account,
                                          metadata=METADATA_FP)
    logging.info(f'Draft transaction written to {raw_matx_path}...')

    # Caculate fees
    fee = calculate_tx_fee(raw_matx_path, protocol_param_fp, input_utxo, receiver)
    logging.info(f'Calculated transaction fee: {fee} lovelace')

    # Adjust fees in lovelace in receiver
    receiver.remove_lovelace(fee)

    # Draft transaction but with fees accounted for
    raw_matx_path = build_raw_transaction(TEMP_DIR,
                                          input_utxo,
                                          receiver,
                                          policy_id,
                                          minting_account,
                                          fee=fee,
                                          metadata=METADATA_FP)
    logging.info(f'Draft transaction with fees written to {raw_matx_path}...')

    # Sign transaction
    signed_matx_path = sign_tx(TEMP_DIR,
                               payment_wallet.get_skey_path(),
                               policy_wallet.get_skey_path(),
                               policy_script_fp,
                               raw_matx_path)
    logging.info(f'Signed transaction written to {signed_matx_path}')

    # Submit transaction to the blockchain
    result = submit_transaction(signed_matx_path)
    if result:
        logging.info(f'Successfully submitted transaction!')
    else:
        logging.info(f'Failed to submit transaction')
