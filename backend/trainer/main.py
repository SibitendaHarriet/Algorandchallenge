import json
import hashlib
import os
import sys
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, wait_for_confirmation
#from closed import closedacc
from algosdk.future.transaction import PaymentTxn
#from created import createdacc
#from utils import *
from tkinter.messagebox import YES
from algosdk import account, mnemonic
from algosdk.v2client import algod
import time

# staff account asset
sys.path.append(os.path.abspath('../'))
#closed account 
def closedacc(algod_client, account):
# build transaction
  
  params = algod_client.suggested_params()
  
  receiver = "QECL3HMPEG4XWX5IKN2JNR3W5TW5EKTFJGE4UWGDGRIGW44ICCWMNNBQIE"
  note = "closing out account".encode()

  # Fifth argument is a close_remainder_to parameter that creates a payment txn that sends all of the remaining funds to the specified address. If you want to learn more, go to: https://developer.algorand.org/docs/reference/transactions/#payment-transaction
  unsigned_txn = PaymentTxn(account["pk"], params, receiver, 0, receiver, note)

  # sign transaction
  signed_txn = unsigned_txn.sign(account["sk"])
  txid = algod_client.send_transaction(signed_txn)
  print('Transaction Info:')
  print("Signed transaction with txID: {}".format(txid))

  # wait for confirmation	
  try:
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round'])) 
  except Exception as err:
    print(err)
    return
  
  account_info = algod_client.account_info(account["pk"])

## created account 
def createdacc(fund=True):
  # Change algod_token and algod_address to connect to a different client
  algod_token = "2f3203f21e738a1de6110eba6984f9d03e5a95d7a577b34616854064cf2c0e7b"
  algod_address = "https://academy-algod.dev.aws.algodev.network/"
  algod_client = algod.AlgodClient(algod_token, algod_address)

  #Generate new account for this transaction
  secret_key, my_address = account.generate_account()
  m = mnemonic.from_private_key(secret_key)
  print("My address: {}".format(my_address))

  # Check your balance. It should be 0 microAlgos
  account_info = algod_client.account_info(my_address)
  print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

  if fund:
    #Fund the created account
    print('Go to the below link to fund the created account using testnet faucet: \n https://dispenser.testnet.aws.algodev.network/?account={}'.format(my_address)) 

    completed = ""
    while completed.lower() != 'yes':
      completed = input("Type 'yes' once you funded the account: ")

    print('Fund transfer in process...')
    # Wait for the faucet to transfer funds
    time.sleep(5)
    
    print('Fund transferred!')
    # Check your balance. It should be 5000000 microAlgos
    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

  return m


accounts = {}
# m = create_account()

m = "iron utility dry subject avocado source plastic scorpion slender theme will maid model improve crack blind resemble business devote mobile venue weekend loud abandon sunny"
accounts[1] = {}
accounts[1]['pk'] = mnemonic.to_public_key(m)
accounts[1]['sk'] = mnemonic.to_private_key(m)

# Change algod_token and algod_address to connect to a different client
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_address = "http://localhost:4001"
algod_client = algod.AlgodClient(algod_token, algod_address)


def create_non_fungible_token():
    print("......................")
    # CREATE ASSET
    # Get network params for transactions before every transaction.
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True


    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = open(dir_path + '/nft.json', "r")

    # Reading from file
    metadataJSON = json.loads(f.read())
    metadataStr = json.dumps(metadataJSON)

    hash = hashlib.new("sha256")
    hash.update(b"arc0003/amj")
    hash.update(metadataStr.encode("utf-8"))
    json_metadata_hash = hash.digest()

    # Account 1 creates an asset called latinum and
    # sets Account 1 as the manager, reserve, freeze, and clawback address.
    # Asset Creation transaction
    txn = AssetConfigTxn(
        sender=accounts[1]['pk'],
        sp=params,
        total=1,
        default_frozen=False,
        unit_name="har10ac",
        asset_name="harriet 10 Academy completion certificate",
        manager=accounts[1]['pk'],
        reserve=None,
        freeze=None,
        clawback=None,
        strict_empty_address_check=False,
        url="https://gateway.pinata.cloud/ipfs/QmXARven5z9VC64kt8ZHwA6R3qT3bfqXkJftJRHZtrNMye",
        metadata_hash=json_metadata_hash,
        decimals=0)

    # Sign with secret key of creator
    stxn = txn.sign(accounts[1]['sk'])

    # Send the transaction to the network and retrieve the txid.
    txid = algod_client.send_transaction(stxn)
    print("Asset Creation Transaction ID: {}".format(txid))

    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(
        confirmed_txn['confirmed-round']))
    try:
        # Pull account info for the creator
        # account_info = algod_client.account_info(accounts[1]['pk'])
        # get asset_id from tx
        # Get the new asset's information from the creator account
        ptx = algod_client.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
        print_created_asset(algod_client, accounts[1]['pk'], asset_id)
        print_asset_holding(algod_client, accounts[1]['pk'], asset_id)
    except Exception as e:
        print(e)

# You have successfully created your own Non-fungible token!
def delete_non_fungible_token(accounts, algod_client, params, asset_id):
    
    # Asset destroy transaction
    txn = AssetConfigTxn(
        sender=accounts[1]['pk'],
        sp=params,
        index=asset_id,
        strict_empty_address_check=False
    )

    # Sign with secret key of creator
    stxn = txn.sign(accounts[1]['sk'])
    # Send the transaction to the network and retrieve the txid.
    txid = algod_client.send_transaction(stxn)
    print("Asset Destroy Transaction ID: {}".format(txid))

    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(
        confirmed_txn['confirmed-round']))
    # Asset was deleted.
    try:
        print_asset_holding(algod_client, accounts[1]['pk'], asset_id)
        print_created_asset(algod_client, accounts[1]['pk'], asset_id)
        print("Asset is deleted.")
    except Exception as e:
        print(e)

 # TRANSFER ASSET
def transfer_non_fungible_token(algod_client, sender, recipient, asset_id):
    # transfer asset of 10 from account 1 to account 3
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True
    txn = AssetTransferTxn(
        sender=sender['pk'],
        sp=params,
        receiver=recipient["pk"],
        amt=1,
        index=asset_id)
    stxn = txn.sign(sender['sk'])
    # Send the transaction to the network and retrieve the txid.
    try:
        txid = algod_client.send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(
            confirmed_txn['confirmed-round']))
    except Exception as err:
        print(err)
    # The balance should now be 10.
    print_asset_holding(algod_client, recipient['pk'], asset_id)

# this is tha account that has opted in...
r = "survey under convince above bind legend cake sniff melt either honey song speed enrich always crew dial mind iron insane ask chat tent abstract life" 
accounts[3] = {}
accounts[3]['pk'] = mnemonic.to_public_key(r)
accounts[3]['sk'] = mnemonic.to_private_key(r)

create_non_fungible_token()
# transfer_non_fungible_token(algod_client, accounts[1], accounts[3], 2)
