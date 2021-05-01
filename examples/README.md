# Example

In this example, we will be minting 5 tokens to demonstrate the use of
the Automint library.

## Quick Start

1. Run the `initialize.py` script via `python initialize.py`.

An output similar to the following will be printed.

```
❯ python initialize.py
INFO:automint.wallet.Wallet:Signing and verification keys for wallet payment not found, generating...
INFO:automint.wallet.Wallet:Address file for wallet payment not found, generating...
INFO:automint.wallet.Wallet:Signing and verification keys for wallet policy not found, generating...
INFO:automint.wallet.Wallet:Address file for wallet policy not found, generating...
INFO:automint.utils.utils:Writing policy script to /Users/lemon/Projects/automint/examples/policy.script
INFO:__main__:Payment wallet address: addr1v909djup82fnvqzf5k0twztapyyq07laatzng95meqd2xpca3e3c0
INFO:__main__:Policy ID: 1406fbb1af2a3f005518e921c016f585a4039b976f7959bfa6ec2486
```

2. Fund the payment wallet.

From the printout from the first step, take note of the payment wallet
address on the second last line. This wallet is created in the
`initialize.py` script and will be used to fund the costs of minting.

A small amount of 4-5 ADA will be plenty for this demo.

3. Run the `mint.py` script via `python mint.py`.

If the transaction has not showed up in the wallet yet, a printout
like the following will be shown. Simply wait about 30 seconds and
then try again.

```
❯ python mint.py
INFO:__main__:Payment wallet address: addr1v909djup82fnvqzf5k0twztapyyq07laatzng95meqd2xpca3e3c0
INFO:__main__:Policy wallet address: addr1v9he0w80hynv9uwu2dnu5yewsa9rtqwvk58e8ypa8fcvaasfudu77
INFO:__main__:No UTXOs found within wallet.
INFO:__main__:Please send some ADA (~5ADA) to the payment wallet address addr1v909djup82fnvqzf5k0twztapyyq07laatzng95meqd2xpca3e3c0
```

If all is successful, you will see a printout similar to the following


```
❯ python mint.py
INFO:__main__:Payment wallet address: addr1v909djup82fnvqzf5k0twztapyyq07laatzng95meqd2xpca3e3c0
INFO:__main__:Policy wallet address: addr1v9he0w80hynv9uwu2dnu5yewsa9rtqwvk58e8ypa8fcvaasfudu77
INFO:__main__:UTXOs found at wallet address...
UTXO: ca324bb0a46a9b96bc5c7b0feaf23159aafd5fe6d39a691412d5171013d67b1c#0
ADA:: 3.0
Contents: {}
INFO:__main__:UTXO to be consumed: ca324bb0a46a9b96bc5c7b0feaf23159aafd5fe6d39a691412d5171013d67b1c#0
INFO:__main__:Protocol parameters written to /Users/lemon/Projects/automint/examples/tmp/protocol.json
INFO:__main__:Policy ID: 1406fbb1af2a3f005518e921c016f585a4039b976f7959bfa6ec2486
INFO:__main__:Draft transaction written to /Users/lemon/Projects/automint/examples/tmp/matx.raw...
INFO:__main__:Calculated transaction fee: 233056 lovelace
INFO:__main__:Draft transaction with fees written to /Users/lemon/Projects/automint/examples/tmp/matx.raw...
INFO:__main__:Signed transaction written to /Users/lemon/Projects/automint/examples/tmp/matx.signed
INFO:__main__:Successfully submitted transaction!
```

4. Check out the new tokens

Via `cardano-cli` we can query the wallet address to see that the
tokens have indeed been minted and deposited back into the wallet.

This can be done by executing the following function `cardano-cli
query utxo --mainnet --address $(cat keys/payment.addr)`.


```
❯ cardano-cli query utxo --mainnet --address $(cat keys/payment.addr)
                           TxHash                                 TxIx        Amount
--------------------------------------------------------------------------------------
78dda92d47e8c39ac55608f73de438be8f328ef19c6e395b766bc6a58cd6f633     0        2766944 lovelace + 1 1406fbb1af2a3f005518e921c016f585a4039b976f7959bfa6ec2486.TestToken00 + 1 1406fbb1af2a3f005518e921c016f585a4039b976f7959bfa6ec2486.TestToken01 + 1 1406fbb1af2a3f005518e921c016f585a4039b976f7959bfa6ec2486.TestToken02 + 1 1406fbb1af2a3f005518e921c016f585a4039b976f7959bfa6ec2486.TestToken03 + 1 1406fbb1af2a3f005518e921c016f585a4039b976f7959bfa6ec2486.TestToken04
```

As seen above, the wallet now contained 2766944 lovelaces which is
about 2.7 ADA and 5 tokens (TestToken00, TestToken01, ...) minted
under the policy ID in step 1.

## Detailed explaination (coming soon...)

Comments have been added liberally within `mint.py` to describe each
function call and block of code. More in-depth explainations will be
written here soon.
