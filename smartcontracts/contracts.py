from pyteal import Addr, And, Global, Int, Mode, Txn, TxnType, compileTeal
import json

BANK_ACCOUNT_FEE = 1000

from helpers import (
    account_balance,
    add_standalone_account,
    create_payment_transaction,
    fund_account,
    process_logic_sig_transaction,
    process_transactions,
    logic_signature,
    suggested_params,
    transaction_info,
)


def bank_for_account(receiver):
    """Only allow receiver to withdraw funds from this contract account.

    Args:
        receiver (str): Base 32 Algorand address of the receiver.
    """
    is_payment = Txn.type_enum() == TxnType.Payment
    is_single_tx = Global.group_size() == Int(1)
    is_correct_receiver = Txn.receiver() == Addr(receiver)
    no_close_out_addr = Txn.close_remainder_to() == Global.zero_address()
    no_rekey_addr = Txn.rekey_to() == Global.zero_address()
    acceptable_fee = Txn.fee() <= Int(BANK_ACCOUNT_FEE)

    return And(
        is_payment,
        is_single_tx,
        is_correct_receiver,
        no_close_out_addr,
        no_rekey_addr,
        acceptable_fee,
    )


def setup_bank_contract(**kwargs):
    """Initialize and return bank contract for provided receiver."""
    receiver = kwargs.pop("receiver", add_standalone_account()[1])

    teal_source = compileTeal(
        bank_for_account(receiver),
        mode=Mode.Signature,
        version=3,
    )
    logic_sig = logic_signature(teal_source)
    escrow_address = logic_sig.address()
    fund_account(escrow_address)
    return logic_sig, escrow_address, receiver


def create_bank_transaction(logic_sig, escrow_address, receiver, amount, fee=1000):
    """Create bank transaction with provided amount."""
    params = suggested_params()
    params.fee = fee
    params.flat_fee = True
    payment_transaction = create_payment_transaction(
        escrow_address, params, receiver, amount
    )
    transaction_id = process_logic_sig_transaction(logic_sig, payment_transaction)
    return transaction_id


if __name__ == "__main__":
    """Example usage for contracts."""

    _, local_receiver = add_standalone_account()
    amount = 5000000
    logic_sig, escrow_address, receiver = setup_bank_contract(receiver=local_receiver)
    assert receiver == local_receiver

    transaction_id = create_bank_transaction(
        logic_sig, escrow_address, local_receiver, amount
    )
    print("amount: %s" % (amount,))
    print("escrow: %s" % (escrow_address))
    print("balance_escrow: %s" % (account_balance(escrow_address),))
    print("balance_receiver: %s" % (account_balance(local_receiver),))
    print(json.dumps(transaction_info(transaction_id), indent=2))

    print("\n\n")