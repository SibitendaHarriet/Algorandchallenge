"""Module for Algorand smart contracts integration testing."""

import base64

import pytest
from algosdk import constants
from algosdk.encoding import encode_address, is_valid_address
from algosdk.error import AlgodHTTPError, TemplateInputError

from contracts import (
    BANK_ACCOUNT_FEE,
    create_bank_transaction,
    setup_bank_contract,
)
from helpers import (
    account_balance,
    add_standalone_account,
    call_sandbox_command,
    transaction_info,
)


def setup_module(module):
    """Ensure Algorand Sandbox is up prior to running tests from this module."""
    call_sandbox_command("up")
    # call_sandbox_command("up", "dev")


class TestBankContract:
    """Class for testing the bank for account smart contract."""

    def setup_method(self):
        """Create receiver account before each test."""
        _, self.receiver = add_standalone_account()

    def _create_bank_contract(self, **kwargs):
        """Helper method for creating bank contract from pre-existing receiver
        and provided named arguments.
        """
        return setup_bank_contract(receiver=self.receiver, **kwargs)

    def test_bank_contract_creates_new_receiver(self):
        """Contract creation function `setup_bank_contract` should create new receiver
        if existing is not provided to it.
        """
        _, _, receiver = setup_bank_contract()
        assert receiver != self.receiver

    def test_bank_contract_uses_existing_receiver_when_it_is_provided(self):
        """Provided receiver should be used in the smart contract."""
        _, _, receiver = self._create_bank_contract()
        assert receiver == self.receiver

    def test_bank_contract_fee(self):
        """Transaction should be created and error shouldn't be raised
        when the fee is equal to BANK_ACCOUNT_FEE.
        """
        logic_sig, escrow_address, receiver = self._create_bank_contract()
        transaction_id = create_bank_transaction(
            logic_sig, escrow_address, receiver, 2000000, fee=BANK_ACCOUNT_FEE
        )
        assert len(transaction_id) > 48

    def test_bank_contract_fee_failed_transaction(self):
        """Transaction should fail when the fee is greater than BANK_ACCOUNT_FEE."""
        fee = BANK_ACCOUNT_FEE + 1000
        logic_sig, escrow_address, receiver = self._create_bank_contract()
        with pytest.raises(AlgodHTTPError) as exception:
            create_bank_transaction(
                logic_sig, escrow_address, receiver, 2000000, fee=fee
            )
        assert "rejected by logic" in str(exception.value)

    def test_bank_contract_raises_error_for_wrong_receiver(self):
        """Transaction should fail for a wrong receiver."""
        _, other_receiver = add_standalone_account()

        logic_sig, escrow_address, _ = self._create_bank_contract()
        with pytest.raises(AlgodHTTPError) as exception:
            create_bank_transaction(logic_sig, escrow_address, other_receiver, 2000000)
        assert "rejected by logic" in str(exception.value)

    @pytest.mark.parametrize(
        "amount",
        [1000000, 500000, 504213, 2500000],
    )
    def test_bank_contract_balances_of_involved_accounts(self, amount):
        """After successful transaction, balance of involved accounts should pass
        assertions to result of expressions calculated for the provided amount.
        """
        logic_sig, escrow_address, receiver = self._create_bank_contract(
            fee=BANK_ACCOUNT_FEE
        )
        escrow_balance = account_balance(escrow_address)
        create_bank_transaction(logic_sig, escrow_address, receiver, amount)

        assert account_balance(receiver) == amount
        assert (
            account_balance(escrow_address)
            == escrow_balance - amount - BANK_ACCOUNT_FEE
        )

    def test_bank_contract_transaction(self):
        """Successful transaction should have sender equal to escrow account.
        Also, the transaction type should be payment, payment receiver should be
        contract's receiver, and the payment amount should be equal to provided amount.
        Finally, there should be no group field in transaction.
        """
        amount = 1000000
        logic_sig, escrow_address, receiver = self._create_bank_contract(
            fee=BANK_ACCOUNT_FEE
        )
        transaction_id = create_bank_transaction(
            logic_sig, escrow_address, receiver, amount
        )
        transaction = transaction_info(transaction_id)
        assert transaction.get("transaction").get("tx-type") == constants.payment_txn
        assert transaction.get("transaction").get("sender") == escrow_address
        assert (
            transaction.get("transaction").get("payment-transaction").get("receiver")
            == receiver
        )
        assert (
            transaction.get("transaction").get("payment-transaction").get("amount")
            == amount
        )
        assert transaction.get("transaction").get("group", None) is None
