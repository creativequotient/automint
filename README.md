# Automint

Python library for automating transactions on the Cardano blockchain.

* Create wallets (and associated signing and verification key files)

* Create policy scripts
  * Basic scripts
  * Time-locked multi-sig scripts

* Build, sign, and submit transactions

* Others
  * Query tip information
  * Query return address from txHash
  * Query stake key associated with address

## Quick start

### Creating wallets

Initialize wallets as follows

```
from automint.wallet import Wallet
wallet = Wallet('wallets', 'payment')
```

The above code will look for `payment.skey` and `payment.vkey` in
`wallets`. If neither are found, then a new set of signing and
verification keys will be generated.

### Querying UTXOs in wallets

Query UTXOs as follows

```
utxos = wallet.query_utxo()
```

A list of `UTXO` objects will be returned, one for the contents of
each UTXO found at the address.

To acquire a UTXO (for spending, as an example), use
`wallet.get_utxo()`. If a suitable UTXO is found (contains more than 5
ADA), one will be returned. If a specific UTXO is desired or if none
meet the threshold for automatic selection, pass the txHash into the
function as follows `wallet.get_utxo(id='<txHash>#<index>')`.

### Token arithmetics

The intuition behind automint is to do arithmetics on UTXOs. Let's
take a look at the following example

```
from automint.receivers import TxReceiver
receiver = TxReceiver('<wallet address>') # wallet address refers to the output address of the transaction

receiver.add_lovelace(10000000)
receiver.add_native_token('12345.sampleToken', 1)
```

First, we create a `TxReceiver` object which deals with the accounting
of a receiver. A receiver represents the output of the transacion (it
is the `--tx-out` field in the CLI command). Then, we add 10000000
lovelace and 1 sampleToken to the receiver.

Subsequently, when we convert the receiver to string representation
via `str(receiver)`, we obtain `<wallet address>+10000000+"1
12345.sampleToken"` which is precisely the format of the input to
`--tx-out`.

The same goes for `MintingReceiver` which formats the output for the
`--mint` argument. Any tokens that will be minted or burnt in the
transaction will need to be added to `MintingReceiver`.

We can convert `UTXO` to `TxReceiver` objects directly by doing
`utxo.convert_to_receiver('<wallet address>)`. This instantiates a
`TxReceiver` object but with all contents of the utxo object
transferred to it. This is particularly useful when sending tokens to
other addresses. Let's take a look at an example.

```
utxo = wallet.get_utxo() # get a UTXO to spend
receiver_a = utxo.convert_to_utxo(wallet.get_address()) # output of this part of the transaction is back to the sending address
receiver_b = TxReceiver('<receipient address>')

receiver_a.remove_lovelace(5000000)
receiver_b.add_lovelace(5000000)
```

Lets assume that originally, `receiver_a` has 10000000 lovelace and 1
token named `12345.sampleToken` in the utxo. Then, at the end of the
above code block, `receiver_a` has 5000000 lovelace and the token
whilst `receiver_b` has 5000000 lovelace. When both are converted to
string representations, we get `<receiver_a address>+5000000+"1
12345.sampleToken"` and `<receiver_b address>+5000000` which are the
exact strings needed for the respective `--tx-out` fields. We can also
see that the balance/output of the transaction perfectly matches the
input amounts.
