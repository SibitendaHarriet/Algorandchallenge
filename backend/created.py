import json
import base64
from tkinter.messagebox import YES
from algosdk import account, mnemonic
from algosdk.v2client import algod
import time

# This is a complete code example that:
#   1. Create a new test account
#   2. Ask to fund your created account

def createdacc(fund=True):
  # Change algod_token and algod_address to connect to a different client
  algod_token = "bbb"
  algod_address = "https://sites.google.com/view/sibitenda-harriet/"
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