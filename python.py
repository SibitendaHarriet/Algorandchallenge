from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn #, wait_for_confirmation
from algosdk.transaction import wait_for_confirmation

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))

generate_algorand_keypair()
#My address: RNYRV6JD6YRFQ4U5KDZER6IAN5I3SMXGGW454PWY6VXYBFZEAAMBPEXO5I
#My private key: QNn8pfXuqXqjSVcHAc3SdKtr7Tni8biGnB0JEwYbOg+LcRr5I/YiWHKdUPJI+QBvUbky5jW53j7Y9W+AlyQAGA==
#My passphrase: chimney vibrant spray urban fatigue team escape firm can cross harvest resemble struggle kitten balcony vehicle strike improve mom correct around man keep abandon powder
harriet = account.generate_account()

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)
#if __name__ == "__main__":
#    print(algod_client.status())
#   print(harriet)
#    print(mnemonic.from_private_key('d9OhHW7nvacddaCYa38xP6WpT6oR6vZFW/aUsWbHYQE12PXuj1r+x81rR4TuLRDXdJneuwgAXse55/5Gmv+8Ag=='))

# CREATE ASSET
# Get network params for transactions before every transaction.
params = algod_client.suggested_params()
# comment these two lines if you want to use suggested params
# params.fee = 1000
# params.flat_fee = True
# Account 1 creates an asset called latinum and
# sets Account 2 as the manager, reserve, freeze, and clawback address.
# Asset Creation transaction
#creator = account.generate_account()
mnemonic_phrase= "athlete inquiry intact erupt dog poverty sentence quick ask laundry sugar helmet glow intact green blush swift youth crash ahead echo urge quality abandon absent"
creator = {
    'pk': 'QECL3HMPEG4XWX5IKN2JNR3W5TW5EKTFJGE4UWGDGRIGW44ICCWMNNBQIE',
    'sk': mnemonic.to_private_key(mnemonic_phrase),
}
txn = AssetConfigTxn(
    sender=creator['pk'],
    sp=params,
    total=1,
    default_frozen=False,
    unit_name="Har10ac",
    asset_name="harriet 10 Academy",
    manager=creator['pk'],
    reserve=creator['pk'],
    freeze=creator['pk'],
    clawback=creator['pk'],
    url="https://harriet10academy.com", 
    decimals=0)
# Sign with secret key of creator
stxn = txn.sign(creator['sk'])
# Send the transaction to the network and retrieve the txid.
#try:
txid = algod_client.send_transaction(stxn)
print("Signed transaction with txID: {}".format(txid))
# Wait for the transaction to be confirmed
confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
print("TXID: ", txid)
print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))   
#except Exception as err:
#    print(err)
# Retrieve the asset ID of the newly created asset by first
# ensuring that the creation transaction was confirmed,
# then grabbing the asset id from the transaction.
#print("Transaction information: {}".format(
#    json.dumps(confirmed_txn, indent=4)))
# print("Decoded note: {}".format(base64.b64decode(
#     confirmed_txn["txn"]["txn"]["note"]).decode()))
try:
    # Pull account info for the creator
    # account_info = algod_client.account_info(accounts[1]['pk'])
    # get asset_id from tx
    # Get the new asset's information from the creator account
    ptx = algod_client.pending_transaction_info(txid)
    asset_id = ptx["asset-index"]
    #print_created_asset(algod_client, accounts[1]['pk'], asset_id)
    #print_asset_holding(algod_client, accounts[1]['pk'], asset_id)
except Exception as e:
    print(e)



#if __name__ == "__main__":